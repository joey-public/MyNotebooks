import googlesearch as goog
from pathlib import Path
import requests
from my_print_util import color_str

trusted_tlds = ['neurips.cc', 'icml.cc', 'ucsd.edu']

def seach_for_paper(s:str)->list:
    print('Searching Google For: ' + color_str(s, 'bold'))
    results = goog.search(s)
    urls = []
    for i, r in enumerate(results):
        urls.append(r)
        if '.pdf' in r:
            print('\t[{}]...{}'.format(color_str(str(i), 'red'),r))
        else:
            print('\t[{}]...{}'.format(i,r))
    return urls

def select_url(urls:list)->str:
    idx = int(input('Enter a Number to Download: '))
    return urls[idx]

def download_pdf(url:str, file_path:str):
    respose = requests.get(url)
    file = Path(file_path)
    file.write_bytes(response.content)

def main():
    papers = ['Serial Order Distributed Processing Jordan paper',
              'Finding Structure in time Elman paper',
              'Generating Text with Reccuent Neural Networks Sutskever',
              'Learning to Generate Reviews and Discovering Sentement',
              'Attention is all you need',
              'Improved Language Understanding by Generative Pre-Training',
              'Language Models are Unsupervised Multitask Learners',
              'Language Models are few-shot Learners',
              'Large Language Models are zero-shot Learners',
              'VOYAGER: An open ended embodied agent with Large Language Models',
              'GPT-4 Technical Report']
    for p in papers:
        all_urls = seach_for_paper(p)
        url = select_url(all_urls)
        do_it = input('About to download from: \n\t{}\nAre you sure?(y/n)'.format(url))
        if do_it == 'y':
            pass

if __name__=="__main__":
    main()
