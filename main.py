#coding: UTF-8
import os
import time
import re

# TWEET
import commands
from twitter import *

# USERSTREAM
from requests_oauthlib import OAuth1Session
import json

# encode
import sys

# TIME_LIMIT
TIME_LIMIT = 1476577800

# input your keys
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""



# @[your screen_name]
ME = ""

def tweet_result(req):
        if req.status_code == 200:
                print ("(main.py: TWITTER.POST) OK")
        else:
                print ("(main.py: TWITTER.POST) Error: %d" % req.status_code)

#======================TWEET_STATUS=========================
def tweet_status(tweet_type, screen_name, reply):
        print "==========================TWEET_STATUS============================"
        url = "https://api.twitter.com/1.1/statuses/update.json"
        url_media = "https://api.twitter.com/1.1/statuses/update_with_media.json"
        url_profile = "https://api.twitter.com/1.1/account/update_profile.json"
        twitter = OAuth1Session(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        print "reply to " + ME
        print "reply from " + screen_name
        print tweet_type

        if "capture" in tweet_type and ME == screen_name:
                if "video0" in tweet_type:
                        dev_video = "/dev/video0"
                elif "video1" in tweet_type:
                        dev_video = "/dev/video1"
                # Webカメラで撮影
                os.system("sudo fswebcam -d " + dev_video + " -r 640x480 sample.jpg");

                files = { 
                        "status" : screen_name + "\n" + dev_video,
                        #"in_reply_to_status_id" : reply,
                        "media[]" : open("sample.jpg","rb")
                }
                req = twitter.post(url_media, files = files)
                tweet_result(req)
        elif "memo" in tweet_type and ME == screen_name:
                date = commands.getoutput("date +\"%Y/%m/%d %H:%M:%S\"")
                context = tweet_type.split(' ', 1)
                os.system("echo \"" + date + " " + context[1] + "\" >> memo.log")
                params = {
                        "status" : screen_name + "\n"+ "(" + date + ") wrote: ...",
                        "in_reply_to_status_id" : reply
                }
                req = twitter.post(url, params = params)
                tweet_result(req)
        elif "update_name" in tweet_type:
                new_name = tweet_type.split(' ', 1)
                params = {
                        "name" : new_name[1]
                }
                req = twitter.post(url_profile, params = params)
                tweet_result(req)
                # tweet result
                if req.status_code != 200:
                        params = {
                                "status" : screen_name + "\n名前の更新に失敗しました.",
                                "in_reply_to_status_id" : reply
                        }
                else:
                        params = {
                                "status" : screen_name + "\n名前を「" + new_name[1] + "」に更
新しました.",
                                "in_reply_to_status_id" : reply
                        }
                date = commands.getoutput("date +\"%Y/%m/%d %H:%M:%S\"")
                cmd = "echo \"" + date + " " + screen_name + " " + new_name[1] + " " + str(req) + "\" >> name.log"
                os.system(cmd)
                req = twitter.post(url, params = params)
                tweet_result(req)
        elif "temperature" in tweet_type:
                # get temperature of raspberry pi
                temperature = commands.getoutput("vcgencmd measure_temp")
                params = {
                        "status" : screen_name + "\n"+ temperature,
                        "in_reply_to_status_id" : reply
                }
                req = twitter.post(url, params = params)
                tweet_result(req)
        elif "speedtest" in tweet_type:
                speedtest = commands.getoutput("speedtest")
                speed_down = re.search('Download:\s\d+\.\d+\sMbit\/s', speedtest)
                speed_up = re.search('Upload:\s\d+\.\d+\sMbit\/s', speedtest)
                speed_result = speed_down.group() + "\n" + speed_up.group()
                params = {
                        "status" : screen_name + "\n" + speed_result,
                        "in_reply_to_status_id" : reply
                }
                req = twitter.post(url, params = params)
                tweet_result(req)
        elif "ouyou" in tweet_type:
                now_time = commands.getoutput("date '+%s'")
                #time_left = TIME_LIMIT - int(now_time)
                #day_left = int(time_left) / 86400

                limit_day = TIME_LIMIT / 86400
                to_day = int(now_time) / 86400
                day_left = limit_day - to_day

                params = {
                        "status" : screen_name + "\n平成28年度秋季応用情報処理技術者試験まで\n" + "残り" + str(day_left) + "日です.",
                        "in_reply_to_status_id" : reply
                }
                req = twitter.post(url, params = params)
                tweet_result(req)
        else:
                print "invalid: " + tweet_type

# ======================================MAIN================================================
if __name__ == '__main__':
        print "(default encoding) " + sys.getdefaultencoding()
        # reload sys because use setdefaultencoding
        reload(sys)
        sys.setdefaultencoding("utf-8")
        print "(set default encoding) " + sys.getdefaultencoding()
        # Stream OAuth
        auth = OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
        twitter_stream = TwitterStream(auth=auth, domain="userstream.twitter.com")
        for msg in twitter_stream.user():
                if "in_reply_to_screen_name" in msg and "text" in msg:
                        if msg["in_reply_to_screen_name"] == "no_run_no_rin":
                                user = msg["user"]
                                reply = msg["id"]
                                content = filter(lambda w: len(w) > 0, re.split(r'\s|\n', msg["text"], 1))
                                #content = msg["text"].split(' ', 1)
                                if len(content) < 2:
                                        continue
                                tweet_status(content[1], "@" + user["screen_name"], reply)
