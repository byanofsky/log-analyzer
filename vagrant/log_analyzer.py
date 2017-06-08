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
            output = curs.fetchall()
    conn.close()
    return output


def get_three_popular_articles():
    sql = '''
        SELECT title, visits
          FROM article_visits
         ORDER BY visits DESC
         LIMIT 3;
    '''
    data = db_op(sql)
    return data


def get_popular_authors():
    sql = '''
        SELECT authors.name AS author_name,
               SUM(article_visits.visits) AS visits
          FROM authors, article_visits
         WHERE authors.id = article_visits.author_id
         GROUP BY authors.id
         ORDER BY visits DESC;
    '''
    data = db_op(sql)
    # Finess data
    f_data = []
    for r in range(len(data)):
        row = data[r]
        f_row = []
        for c in range(len(row)):
            if c == 1:
                cell = '{} views'.format(row[c])
            else:
                cell = row[c]
            f_row.append(cell)
        f_data.append(f_row)
    return f_data


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
    error_data = get_error_data()
    formatted_error_data = format_data(error_data)
    error_table = create_table(formatted_error_data, 'Error Report')
    print(error_table)

    articles_data = get_three_popular_articles()
    formatted_articles_data = format_data(articles_data)
    popular_articles_table = create_table(formatted_articles_data,
                                          'Popular Articles')
    print(popular_articles_table)
    #
    # error_data = get_error_report()
    # print('\n\n'+create_table(error_data, 'Complete Error Report')+'\n\n')

    # error_data = get_error_report(0.01)
    # print('\n\n'+create_table(error_data, 'Error Report > 1%')+'\n\n')

    # author_data = get_popular_authors()
    # print('\n\n'+create_table(author_data, 'Popular Authors')+'\n\n')
    # print(get_widest_cols(three_popular_articles()))
    # print(get_widest_cols(error_report()))
    # print(get_widest_cols(popular_authors()))


# # Get count of path visits for 200 status only
# SELECT log.path, COUNT(log.id)
#   FROM log
#  WHERE log.status = '200 OK'
#  GROUP BY log.path;
#
# # slug visit count (200 only)
# CREATE VIEW slug_visits AS
#        SELECT log.path AS slug,
#               COUNT(log.id) AS visits
#          FROM log
#         WHERE log.status = '200 OK'
#         GROUP BY log.path;
#
# # most popular articles
# SELECT articles.title AS title,
#        slug_visits.slug AS slug,
#        slug_visits.visits AS visits
#   FROM articles, slug_visits
#  WHERE slug_visits.slug = '/article/' || articles.slug
#  ORDER BY visits DESC;
#
# # article visits
# CREATE VIEW article_visits AS
#        SELECT articles.id AS article_id,
#               articles.title AS title,
#               articles.author AS author_id,
#               slug_visits.slug AS slug,
#               slug_visits.visits AS visits
#          FROM articles, slug_visits
#         WHERE slug_visits.slug = '/article/' || articles.slug
#         ORDER BY visits DESC;
#
# # 3 most popular articles
# SELECT title, visits
#   FROM article_visits
#  ORDER BY visits DESC
#  LIMIT 3;
#
# # Popular authors with count
# SELECT authors.name AS author_name,
#        authors.id AS author_id,
#        SUM(article_visits.visits) AS visits
# FROM authors, article_visits
# WHERE authors.id = article_visits.author_id
# GROUP BY authors.id
# ORDER BY visits DESC;
#
# # Convert date to char
# to_char(date_trunc('day', log.time), 'Month DD, YYYY')
#
# # Total visits by day
# CREATE VIEW day_visits_total AS
#      SELECT date_trunc('day', log.time) AS day,
#             COUNT(log.id)
#        FROM log
#       GROUP BY day;
#
# # Success visits by day
# CREATE VIEW day_visits_success AS
#      SELECT date_trunc('day', log.time) AS day,
#             COUNT(log.id)
#        FROM log
#       WHERE log.status = '200 OK'
#       GROUP BY day;
#
# # Error visits each day
# CREATE VIEW day_visits_errors AS
#      SELECT date_trunc('day', log.time) AS day,
#             COUNT(log.id)
#        FROM log
#       WHERE log.status != '200 OK'
#       GROUP BY day;
#
# # Show all log visits
# SELECT day_visits_total.day as day,
#        day_visits_total.count as total,
#        day_visits_errors.count as errors,
#        day_visits_success.count as success,
#        day_visits_errors.count + day_visits_success.count = day_visits_total.count as check
#   FROM day_visits_total,
#        day_visits_errors,
#        day_visits_success
#  WHERE day_visits_total.day = day_visits_errors.day
#        AND day_visits_total.day = day_visits_success.day;
#
# # Show percentage of errors
# SELECT day_visits_total.day as day,
#        CAST(day_visits_errors.count AS real) / day_visits_total.count as error_perc
#   FROM day_visits_total,
#        day_visits_errors
#  WHERE day_visits_total.day = day_visits_errors.day
#        AND CAST(day_visits_errors.count AS real) / day_visits_total.count > 0.01;
