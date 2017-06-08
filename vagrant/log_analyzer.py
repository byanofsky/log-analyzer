import psycopg2
import datetime
from table_maker import create_table


def db_op(sql=None, data=None):
    if not sql:
        print('No SQL query. Returning empty.')
        return
    # Connect to an existing database
    conn = psycopg2.connect("dbname=news user=vagrant")
    with conn:
        with conn.cursor() as curs:
            curs.execute(sql, data)
            if curs.description == None:
                output = None
            else:
                output = curs.fetchall()
    conn.close()
    return output


def init_db():
    # Create view for total requests per day per status code (200 or 404)
    db_op('''
        CREATE OR REPLACE VIEW req_by_day_status AS
            SELECT date_trunc('day', log.time) AS day,
                   log.status,
                   CAST(COUNT(log.id) AS bigint) AS reqs
              FROM log
             GROUP BY day, status;
    ''')
    # Create view for total requests per day
    db_op('''
        CREATE OR REPLACE VIEW req_by_day AS
            SELECT day,
                   CAST(SUM(reqs) AS bigint) AS reqs
              FROM req_by_day_status
             GROUP BY day;
    ''')
    # Create view for errors (404) per day
    db_op('''
        CREATE OR REPLACE VIEW error_by_day AS
            SELECT day,
                   CAST(SUM(reqs) AS bigint) AS reqs
              FROM req_by_day_status
             WHERE status != '200 OK'
             GROUP BY day;
    ''')
    # Create view for error percentage by day
    db_op('''
        CREATE OR REPLACE VIEW error_perc_by_day AS
            SELECT total.day,
                   SUM(error.reqs) AS errors,
                   SUM(total.reqs) AS reqs,
                   SUM(error.reqs) / SUM(total.reqs) AS error_perc
            FROM req_by_day AS total,
                 error_by_day AS error
            WHERE total.day = error.day
            GROUP BY total.day;
    ''')
    # Create view with visits by article id/name
    db_op('''
        CREATE OR REPLACE VIEW articles_views AS
            SELECT articles.id,
                   articles.title,
                   articles.author AS author_id,
                   count(log.id) AS views
              FROM articles, log
             WHERE log.path = '/article/' || articles.slug
             GROUP BY articles.id
             ORDER BY views DESC;
    ''')
    print('Database initialized')


def get_three_popular_articles():
    sql = '''
        SELECT title,
               views
          FROM articles_views
         LIMIT 3;
    '''
    data = db_op(sql)
    return data


def get_popular_authors():
    sql = '''
        SELECT authors.name,
               SUM(articles_visits.visits) as visits
          FROM articles_visits,
               authors
         WHERE authors.id = articles_visits.author_id
         GROUP BY authors.name
         ORDER BY visits DESC;
    '''
    data = db_op(sql)
    return data


def get_error_data(min=0):
    sql = '''
        SELECT day_visits_total.day AS day,
               CAST(day_visits_errors.count AS real) / day_visits_total.count AS error_perc
          FROM day_visits_total,
               day_visits_errors
         WHERE day_visits_total.day = day_visits_errors.day
               AND CAST(day_visits_errors.count AS real) / day_visits_total.count > %s;
    '''
    data = (str(min),)
    output = db_op(sql, data)
    return output


def format_data(data):
    output = []
    for r in data:
        output_row = []
        for c in r:
            if type(c) is datetime.datetime:
                output_cell = c.strftime('%B %d, %Y')
            elif type(c) is float:
                perc = c * 100
                output_cell = '{:.2f}%'.format(perc)
            elif type(c) is long:
                output_cell = '{} views'.format(c)
            else:
                output_cell = c
            output_row.append(output_cell)
        output.append(output_row)
    return output


if __name__ == '__main__':
    articles_data = get_three_popular_articles()
    formatted_articles_data = format_data(articles_data)
    popular_articles_table = create_table(formatted_articles_data,
                                          'Popular Articles')
    print(popular_articles_table)

    author_data = get_popular_authors()
    formatted_author_data = format_data(author_data)
    authors_table = create_table(formatted_author_data, 'Popular Authors')
    print(authors_table)

    error_data = get_error_data(0.01)
    formatted_error_data = format_data(error_data)
    error_table = create_table(formatted_error_data, 'Error Report > 1%')
    print(error_table)
