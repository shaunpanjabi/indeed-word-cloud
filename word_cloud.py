#############################################################################################
# Indeed Word Cloud Creator
# Author: Shaun Panjabi
#
# Description:
#   -Allows you to create a word cloud of jobs from a list of queries. The current behavior is to
#    get the first 25 job queries it finds for each of the 385 cities in the United States.
#
# See Indeed Python docs here: https://github.com/indeedlabs/indeed-python
# Blog post: https://shaunlp.wordpress.com/2015/12/30/indeed-word-cloud/
#
#############################################################################################
from indeed import IndeedClient
from collections import Counter
from sys import stdout
import requests
import pprint

def build_params(locations, job_query):
    """
    Function to build parameters for list of location for a specific job query.

    :param locations: {list} list of locations to search
    :param job_query: {str} job description to search
    :return: list of params usable by Indeed API
    """
    params = {
        'q' : job_query,
        'l' : '',
        'userip' : "1.2.3.4",
        'useragent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
        "limit" : 25
    }

    param_list = []
    for location in locations:
        params = params.copy()
        params['l'] = location.lower()
        param_list.append(params)
    return param_list

def pull_job_description(html_content):
    """
    Function to remove content that isn't the job description, and filter out html tags

    :param html_content: {str} string of html content.
    :return: {str} filtered result
    """
    remove_left = html_content.split('<span id="job_summary" class="summary">')
    if len(remove_left) > 1:
        remove_left = remove_left[1]
        remove_right = remove_left.split('</span>')[0]
        cleanup = ['<br>','<ul>' ,'</ul>', '<li>', '</li>', '<b>', '</b>' , '<em>', '<br/>', '</p>', '<p>' , '(', ')', ';', ',' , ':']

        for code in cleanup:
            remove_right = remove_right.replace(code, ' ')
    else:
        print("Something went wrong, discarding result...")
        remove_right = ''
    return remove_right.split()

def load_cities(file):
    '''
    Loads words line by line from a .txt file

    :param file: {str} file path
    :return: {list} list of each line of file
    '''
    with open(file) as f:
        content = [x.strip('\n') for x in f.readlines()]
    return content

def save_to_file(file, counter):
    '''
    Saves a Counter object in order of most common to a text file.

    :param file: {str} name of output file
    :param counter: {Counter} counter object used
    :return: none
    '''
    ordered_counter = counter.most_common()
    with open(file, 'w') as f:
        for word in ordered_counter:
            line = str(word[1]) + ' -> ' + str(word[0]) + '\n'
            f.write(line)

# CHANGE THESE PARAMETERS
PUB_ID = "YOUR INDEED PUBLISHER ID GOES HERE"
OUTPUT_FILE = "output.txt"
JOB_QUERY = 'android'
locations = load_cities('list_of_cities.txt')

def main():
    client = IndeedClient(PUB_ID)
    search_params = build_params(locations, JOB_QUERY)

    search_results = []
    count = 1
    for params in search_params:
        stdout.flush()
        stdout.write("\rHtml request: {}/{}".format(count, len(locations)))
        search_response = client.search(**params)
        search_results.append(search_response)
        count += 1

    word_filter = ['and', 'to', 'the', 'of', 'a', 'in', 'with', 'you', 'on', 'that', 'are', 'will', 'is', 'your', 'for',
                   'we', 'from', 'an', 'be', 'have', 'or', 'just', 'can', 'also', 'how', 'at', 'as', 'do', 'other',
                   'should', 'what', 'us', 'this', 'it', 'if', 'get', '-', '&', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                   'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    count = 1
    number_of_locations = len(search_results)
    word_map = Counter()

    for search in search_results:
        print "Currently on {}/{}".format(count, number_of_locations)
        if len(search['results']) == 0:
            print "Nothing found for: {}".format(search['location'])
        else:
            print "Attempting {}...".format(search['location'])
        for job in search['results']:
            url = job['url']
            html = requests.get(url)
            word_list = pull_job_description(html.content)

            for word in word_list:
                if word.lower() not in word_filter:
                    word_map[word.lower()] += 1
        count += 1

        save_to_file(OUTPUT_FILE, word_map)

if __name__ == '__main__':
    main()
    print "done"