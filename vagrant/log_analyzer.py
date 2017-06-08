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
            try:
                output = curs.fetchall()
            except psycopg2.ProgrammingError as e:
                print(e)
                output = None
    conn.close()
    return output


def init_db():
    view_total_visits = '''
        CREATE OR REPLACE VIEW day_visits_total AS
             SELECT date_trunc('day', log.time) AS day,
                    COUNT(log.id)
               FROM log
              GROUP BY day;
    '''
    db_op(view_total_visits)

    view_error_visits = '''
        CREATE OR REPLACE VIEW day_visits_errors AS
             SELECT date_trunc('day', log.time) AS day,
                    COUNT(log.id)
               FROM log
              WHERE log.status != '200 OK'
              GROUP BY day;
    '''
    db_op(view_error_visits)




def get_three_popular_articles():
    sql = '''
        SELECT articles.title,
               count(log.id) as visits
          FROM articles,
               log
         WHERE log.path = '/article/' || articles.slug
         GROUP BY articles.title
         ORDER BY visits DESC
         LIMIT 3;
    '''
    data = db_op(sql)
    return data


def get_popular_authors():
    sql = '''
        SELECT authors.name,
               count(log.id) as visits
          FROM articles,
               authors,
               log
         WHERE log.path = '/article/' || articles.slug
               AND authors.id = articles.author
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

    error_data = get_error_data()
    formatted_error_data = format_data(error_data)
    error_table = create_table(formatted_error_data, 'Error Report')
    print(error_table)
