import psycopg2


def db_op(sql=None):
    if not sql:
        print('No SQL query. Returning empty.')
        return
    # Connect to an existing database
    conn = psycopg2.connect("dbname=news user=vagrant")
    with conn:
        with conn.cursor() as curs:
            curs.execute(sql)
            data = curs.fetchall()
    conn.close()
    return data


def three_popular_articles():
    sql = '''
        SELECT title, visits
          FROM article_visits
         ORDER BY visits DESC
         LIMIT 3;
    '''
    formatted = []
    data = db_op(sql)
    longest_row = 0
    for d in data:
        row = '| {} | {} views |'.format(d[0], d[1])
        formatted.append(row)
        longest_row = max(len(row), longest_row)
    title = 'Most Popular Articles'
    formatted.insert(0, '-' * longest_row)
    formatted.insert(0, '| ' + title + (' ' * (longest_row-len(title)-4)) + ' |')
    formatted.insert(0, '-' * longest_row)
    formatted.append('-' * longest_row)
    return '\n'.join(formatted)

if __name__ == '__main__':
    print(three_popular_articles())

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
