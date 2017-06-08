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
    # Create view for count by day by status code
    view_visits_by_status = '''
        CREATE OR REPLACE VIEW visits_by_day_status AS
            SELECT date_trunc('day', log.time) AS day,
                   log.status,
                   COUNT(log.id) as views
             FROM log
            GROUP BY day, status;
    '''
    db_op(view_visits_by_status)
    # Create view for count of total visits by day
    view_total_visits = '''
        CREATE OR REPLACE VIEW visits_by_day AS
             SELECT day,
                    SUM(views) as views
               FROM visits_by_day_status
              GROUP BY day;
    '''
    db_op(view_total_visits)
    # Create view for count of errors by day
    view_error_visits = '''
        CREATE OR REPLACE VIEW error_visits_by_day AS
             SELECT day,
                    views
               FROM visits_by_day_status
              WHERE status != '200 OK';
    '''
    db_op(view_error_visits)
    # Create view with visits by article id/name
    view_articles_visits = '''
        CREATE OR REPLACE VIEW articles_visits AS
            SELECT articles.id,
                   articles.title,
                   articles.author as author_id,
                   count(log.id) as visits
                FROM articles, log
                WHERE log.path = '/article/' || articles.slug
                GROUP BY articles.id
                ORDER BY visits DESC;
    '''
    db_op(view_articles_visits)
    print('Database initialized')


def get_three_popular_articles():
    sql = '''
        SELECT title,
               visits
          FROM articles_visits
         LIMIT 3;
    '''
    data = db_op(sql)
    return data


def get_popular_authors():
    sql = '''
        SELECT articles_visits.title,
               authors.name,
               articles_visits.visits as visits
          FROM articles_visits,
               authors
         WHERE authors.id = articles_visits.author_id
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
