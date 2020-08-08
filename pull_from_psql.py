import psycopg2
import csv

conn_string = """dbname='exampledb' user='cathyzhou@cathydb2' host='cathydb2.postgres.database.azure.com' password='3.14159Zyr' port='5432' sslmode='require'"""
# Construct connection string


def get_data(conn_string):
    conn = psycopg2.connect(conn_string) 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iris;")
    rows = cursor.fetchall()

    with open('data.csv', 'w') as f:
        fieldnames = ['sepal_length', 'sepal_width','peta_length','petal_width','class']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in rows:
            writer.writerow({'sepal_length': i[0], 'sepal_width': i[1],'peta_length': i[2],'petal_width': i[3],'class': i[4]})



if __name__ == '__main__':
    get_data(conn_string)