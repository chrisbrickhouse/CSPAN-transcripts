# Copyright 2021 Christian Brickhouse
#
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse

from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By

def getTranscriptChunk(tds,browser):
    transcriptChunk = []
    for td in tds:
        if td.get_attribute('class') == 'image':
            continue
        try:
            a = td.find_element(By.CLASS_NAME, 'hidden-full-transcript-link')
            browser.execute_script("arguments[0].click();",a)
        except:
            pass
        # Following isn't quite correct; some transcript text is
        #  in elements without the stated class
        chunks = td.find_elements(By.CLASS_NAME, 'transcript-time-seek')
        for chunk in chunks:
            if chunk.text.strip() == "":
                continue
            transcriptChunk.append(chunk.text)
    return(" ".join(transcriptChunk))

def getTimestamp(row):
    header = row.find_element(By.TAG_NAME, 'th')
    stamp = [int(x) for x in header.text.split(':')]
    t = timedelta(hours=stamp[0],minutes=stamp[1], seconds=stamp[2])
    return(t.total_seconds())

def faveOutput(chunks, times):
    rows = []
    for i in range(len(chunks)):
        row = ['?', '?', str(times[i]), str(times[i+1]), str(chunks[i])]
        rows.append('\t'.join(row))
    return('\n'.join(rows))

def main(url, outName):
    ffops = webdriver.FirefoxOptions()
    ffops.headless = True
    browser = webdriver.Firefox(options=ffops)

    browser.get(url)

    duration = browser.find_element(By.CLASS_NAME, 'jw-video-duration').text
    dur = [int(x) for x in duration.split(':')]
    duration = timedelta(hours=dur[0],minutes=dur[1],seconds=dur[2]).total_seconds()

    sec = browser.find_element_by_class_name('transcript')
    rows = sec.find_elements(By.TAG_NAME, 'tr')
    transcript = []
    times = []
    for row in rows:
        tds = row.find_elements(By.TAG_NAME, 'td')
        chunk = getTranscriptChunk(tds,browser)
        time = getTimestamp(row)
        transcript.append(chunk)
        times.append(time)
    browser.close()
    times.append(duration)

    outText = faveOutput(transcript,times)

    with open(outName, 'w') as f:
        f.write(outText)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("url", help="The cspan url to get a transcript from.")
    parser.add_argument("output", help="Name of file that transcript should be written to.")
    args = parser.parse_args()
    main(args.url, args.output)

