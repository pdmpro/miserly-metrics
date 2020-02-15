"""
Lambda that accepts input from the miserlyMetrics client and saves values to a MySQL (AWS RDS).
Uses the AWS API Gateway, upon which you'll have to configure CORS permissions.

Requires pymysql module: https://github.com/PyMySQL/PyMySQL
And that requires the cryptography module: https://pypi.org/project/cryptography/
"""

from __future__ import print_function
import logging
import os
import boto3
import json
import decimal
import uuid
import datetime
import pymysql

# MySQL settings
mysql_info = {
    "host": "YOUR_MYSQL_HOST.YOUR_REGION.rds.amazonaws.com",
    "username": "YOUR_MYSQL_UN",
    "pwd": "YOUR_MYSQL_PWD",  # Hey! You don't have to keep the password here. And shouldn't. AWS has a way to store secrets for use in Lambdas.
    "db": "YOUR_MYSQL_DATABASE",
    "conn_timeout": 15,
    "table": "MetricsSummary"
}

def lambda_handler(event, context):
    base_response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        }
    }
    if event["httpMethod"] == "OPTIONS":
        # for CORS purposes, only need return the headers and status code
        return base_response
    elif event["httpMethod"] == "POST":
        return do_stuff(base_response, event, context)
    else:
        # probably a GET, which is invalid for my purposes
        base_response["body"] = json.dumps({"success":False, "exception":"POST required"})
        return base_response

def do_stuff(response, event, context):
    # if we get here, we've got a post request and it damn well better have a body
    req_body = json.loads(event["body"])
    affected_record_count = post_to_mysql(req_body)
    response["body"] = json.dumps({"success":True, "count":affected_record_count})
    return response

def post_to_mysql(item):
    try:
        connection = pymysql.connect(
            mysql_info["host"],
            user=mysql_info["username"],
            passwd=mysql_info["pwd"],
            db=mysql_info["db"],
            connect_timeout=mysql_info["conn_timeout"]
        )
    except StandardError as e:
        logging.error("ERROR: Could not connect to MySQL with settings {}\n{}".format(mysql_info, e))
        raise FailedSQLConnectionError()

    # compose the insert (trickily uses a fieldnames list as a shortcut)
    fieldnames = [
        "created",
        "pageId",
        "hostname",
        "clicks",
        "mouseleaves",
        "mousemoveHalts",
        "mousemovePixels",
        "resizeHalts",
        "resizePixels",
        "scrollHalts",
        "scrollPixels"
    ]
    sql = "INSERT INTO {table}({cols}) VALUES ({vp})".format(
        table=mysql_info["table"],
        cols=",".join(fieldnames),
        vp=("%s," * len(fieldnames))[:-1]
    )
    # the order of these values really matters! must match the fieldnames list
    values = (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),          # created, in MySQL format: 2019-02-27 10:28:01
        item["page"],                                                   # page identifier
        item["host"],                                                   # hostname
        item["uxMetrics"]["summaries"]["click"]["fireCount"],           # clicks
        item["uxMetrics"]["summaries"]["mouseleave"]["fireCount"],      # mouseleaves
        item["uxMetrics"]["summaries"]["mousemove"]["stateChangeCount"],# mousemoveHalts
        item["uxMetrics"]["summaries"]["mousemove"]["fireCount"],       # mousemovePixels
        item["uxMetrics"]["summaries"]["resize"]["stateChangeCount"],   # resizeHalts
        item["uxMetrics"]["summaries"]["resize"]["fireCount"],          # resizePixels
        item["uxMetrics"]["summaries"]["scroll"]["stateChangeCount"],   # scrollHalts
        item["uxMetrics"]["summaries"]["scroll"]["fireCount"],          # scrollPixels
    )
    # do the INSERT
    record_count = 0
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
            connection.commit()
            record_count = cursor.rowcount
    except pymysql.IntegrityError as e:
        logging.error("ERROR: Failed INSERT:\n{}".format(e))
        raise InsertionError(e[1])
    finally:
        connection.close()
    return record_count

class PyUXMetricsError(Exception):
    # base class for my custom exceptions, because the Python gods demand some arbitrary base class
    pass

class FailedSQLConnectionError(PyUXMetricsError):
    # for when MySQL doesn't like me
    def __init__(self):
        super(FailedSQLConnectionError, self).__init__("Failed to connect to database.")

class InsertionError(PyUXMetricsError):
    def __init__(self, sql_error_msg, *args):
        super(SQLError, self).__init__("Failed to insert into database: {}".format(sql_error_msg))
