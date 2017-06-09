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
psql -d news -f newsdata.sql
```
5. Run the analyzer:
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

## Built With

* [psycopg](http://initd.org/psycopg/)

## Acknowledgments

Original virtual machine from [Udacity](https://github.com/udacity/fullstack-nanodegree-vm)
