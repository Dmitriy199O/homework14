import sqlite3
from flask import Flask, jsonify


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True

    def db_connect(query):
        con = sqlite3.connect("netflix.db")
        cur = con.cursor()

        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    @app.route('/movie/<title>')
    def serach_by_title(title):
        query = (f"""
                      SELECT  title,country,release_year,description,listed_in AS genre
                      FROM netflix
                      WHERE title = '{title}'
                      ORDER BY release_year DESC
                      LIMIT 1
                  """)
        res = db_connect(query)[0]
        res_json = dict(title=res[0], country=res[1], release_year=res[2], genre=res[4], description=res[3].strip())
        return jsonify(res_json)

    @app.route('/movie/<int:beginning>/to/<int:ending>')
    def search_by_title(beginning, ending):
        query = (f"""
                          SELECT  title,release_year
                          FROM netflix
                          WHERE release_year BETWEEN '{beginning}' AND '{ending}'
                          ORDER BY release_year DESC
                          LIMIT 100
                  """)
        res = db_connect(query)
        res_json = []
        for r in res:
            i = dict(title=r[0], release_year=r[1])
            res_json.append(i)

        return jsonify(res_json)

    @app.route('/rating/<group>')
    def search_by_rating(group):
        levels = {
            'children': ['G'],

            'family': ['G', 'PG', 'PG-13'],

            'adult': ['R', 'NC-17']
        }

        if group in levels:
            level = '\",\"'.join(levels[group])
            level = f'\"{level}\"'

        query = (f"""
                  SELECT title,rating,description
                  FROM netflix
                  WHERE rating IN ({level})         
             """)
        res = db_connect(query)
        res_json = []
        for r in res:
            res_json.append({
                'title': res[0],
                'rating': res[1],
                'description': res[2],
            })

        return jsonify(res_json)

    @app.route('/genre/<genre>')
    def get_newest(genre):

        query = (f"""
                SELECT title,description
                FROM netflix
                WHERE listed_in LIKE '%{genre}%'
                ORDER BY release_year DESC
                LIMIT 10

               """)

        res = db_connect(query)
        res_json = []
        for r in res:
            res_json.append({
                'title': res[0],
                'description': res[1],
            })
        return jsonify(res_json)

    def get_by_actors(name1='Jack Black', name2='Dustin Hoffman'):

        query = (f"""
                   SELECT cast
                   FROM netflix
                   WHERE cast LIKE '%{name1}%'
                   AND cast LIKE '%{name2}'       
                """)
        result = db_connect(query)

        actors = []

        for r in result:
            actors.extend(r[0].split(', '))
        res = []
        for actor in actors:
            if actor not in [name1, name2]:
                if actors.count(actor) > 2:
                    res.append(actor)
        res = set(res)
        return res

    def search_by_type_genre_year(type,year,genre):

        query = (f"""
                    SELECT title,description
                    FROM netflix
                    WHERE type='{type}'
                    AND release_year = '{year}'
                    AND listed_in LIKE '%{genre}%'
                    
                  """)

        result=db_connect(query)
        res_json = []
        for r in result:
            r_ = {'title': r[0],
                  'description': r[1]
                  }
            res_json.append(r_)

    app.run(debug=True)



if __name__ == "__main__":
    main()
