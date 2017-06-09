# Log Analyzer

Analyzes a server's log files to uncover most popular posts and most popular authors.

## Motivation

This is a project from Udacity's Full Stack Nanodegree program. Its intent is to show how SQL can be used to analyze a website log.

## Getting Started

Provided you'll find a Vagrant environment with all dependencies.

### Prerequisites

To run Vagrant, you will need to install [Vagrant](https://www.vagrantup.com/intro/getting-started/install.html) and [VirtualBox](https://www.virtualbox.org).

### Installing

From within the project root:

1. Start Vagrant environment
```
$ cd vagrant
$ vagrant up
```
It can take a little while for this to complete since it needs to download and install everything
2. SSH into Vagrant environment:
```
$ vagrant ssh
```
3. Change to project directory
```
$ cd /vagrant
```
4. Load data into the `news` database. A test log is included:
```
$ psql -d news -f newsdata.sql
```
5. Create database views:
```
$ python3 create_db_views.py
```
6. Run the analyzer:
```
$ python3 log_analyzer.py
```

If all works, you should get 3 tables like this:
```
----------------Popular Articles-----------------

 Candidate is jerk, alleges rival | 338647 views
-------------------------------------------------
 Bears love berries, alleges bear | 253801 views
-------------------------------------------------
 Bad things gone, say good people | 170098 views
```

## Design

Data is retrieved from the database using 3 functions:
```
# Returns 3 most popular articles
get_three_popular_articles()

# Returns a list of all authors, in order of popularity (number of views)
get_popular_authors()

# Returns the percentage of errors (404 errors / total request) grouped by day
# min is the minimum error percentage to filter
get_error_data(min=0)
```

There is also a helper module called `table_maker` to handle formatting the data

## Built With

* [psycopg](http://initd.org/psycopg/)

## Acknowledgments

Original virtual machine from [Udacity](https://github.com/udacity/fullstack-nanodegree-vm)
