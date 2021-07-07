# create views for sqlite db

import sqlite3
import yaml

# path = "/home/michal/project/pollster.eu/dev/datasette/create/"
path = "/home/michal/project/mandaty.cz/api/create/"

settings = yaml.safe_load(open(path + "settings.yaml"))

conn = sqlite3.connect(settings['path'] + settings['db_path'] + "data.sqlite")
curs = conn.cursor()

# query = 'DROP VIEW last_term_polls;'
# curs.execute(query)

query = '''
    CREATE VIEW IF NOT EXISTS last_term_polls(pollster_id, pollster_name, pollster_abbreviation, pollster_link, pollster_score, poll_identifier, poll_link, poll_start_date, poll_end_date, poll_published_date, poll_population, poll_sponsor, poll_method, poll_n, poll_area, question_open, question_question, question_n)
    AS
    SELECT p.id as pollster_id, p.name as pollster_name, p.abbreviation as pollster_abbreviation, p.link as pollster_link, p.score as pollster_score,
    po.identifier as poll_identifier, po.link as poll_link, po.start_date as poll_start_date, po.end_date as poll_end_date, po.published_date as poll_published_date, po.population as poll_population, po.sponsor as poll_sponsor, po.method as poll_method, po.n as poll_n, po.area as poll_area,
    q.open as question_open, q.question as question_question, q.n as question_n
    FROM questions as q
    LEFT JOIN polls as po
    ON q.pollster_id = po.pollster_id AND q.poll_identifier = po.identifier
    LEFT JOIN pollsters as p
    ON po.pollster_id = p.id
    WHERE q.identifier = "model"
    AND po.end_date > "%(led)s"
    ORDER BY po.end_date DESC
''' % {'led': settings['last_election_date']}

curs.execute(query)
conn.commit()
rows = curs.fetchall()

for row in rows:
    print(row)

# query = "SELECT * FROM last_term_polls"
# curs.execute(query)
# conn.commit()
# rows = curs.fetchall()

# for row in rows:
#     print(row)

# query = 'DROP VIEW last_term_data;'
# curs.execute(query)

query = '''
    CREATE VIEW IF NOT EXISTS last_term_data(question_identifier, poll_identifier, pollster_id, choice_id, topic_id, value, poll_end_date, choice_name, choice_abbreviation, pollster_score, color_color)
    AS
    SELECT d.*, po.end_date as poll_end_date, c.name as choice_name, c.abbreviation as choice_abbreviation,
    p.score as pollster_score, co.color as color_color
    FROM data as d
    LEFT JOIN choices as c
    ON d.choice_id = c.id
    LEFT JOIN polls as po
    ON d.poll_identifier = po.identifier AND d.pollster_id = po.pollster_id
    LEFT JOIN pollsters as p
    ON d.pollster_id = p.id
    LEFT JOIN colors as co
    ON c.abbreviation = co.abbreviation
    WHERE d.question_identifier = "model"
    AND po.end_date > "%(led)s"
    ORDER BY po.end_date DESC, d.value DESC
'''  % {'led': settings['last_election_date']}
curs.execute(query)
conn.commit()

# query = 'DROP TABLE last_term_moving_averages;'
# curs.execute(query)

query = '''
    CREATE TABLE IF NOT EXISTS last_term_moving_averages (
        question_identifier,
        pollster_id,
        pollster_score,
        poll_identifier,
        poll_end_date,
        choice_id,
        choice_name,
        choice_abbreviation,
        topic_id,
        value,
        color_color
    );
'''
curs.execute(query)
query = "CREATE UNIQUE INDEX last_term_moving_averages_pollster_id_poll_identifier_choice_abbreviation ON last_term_moving_averages(pollster_id, poll_identifier, choice_abbreviation);"
curs.execute(query)
conn.commit()
#
# rows = curs.fetchall()
#
# for row in rows:
#     print(row)


query = '''
    CREATE TABLE IF NOT EXISTS last_seat_predictions (

    );
'''
