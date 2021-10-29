'''
    Cumination
    Copyright (C) 2021 Team Cumination

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
from six.moves import urllib_parse
from resources.lib import utils
from resources.lib.adultsite import AdultSite

site = AdultSite('perverzija', '[COLOR hotpink]Perverzija[/COLOR]', 'https://tube.perverzija.com/', 'https://tube.perverzija.com/wp-content/uploads/2018/12/favico2.ico', 'perverzija')


@site.register(default_mode=True)
def Main():
    site.add_dir('[COLOR hotpink]Tags[/COLOR]', site.url + 'tags/', 'Tag', site.img_cat)
    List(site.url + 'page/1/')


@site.register()
def List(url):
    listhtml = utils.getHtml(url)
    match = re.compile(r'<a href="([^"]+)">\s*?<img.*?src="([^"]+)".*?title="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for videourl, img, name in match:
        name = utils.cleantext(name)
        site.add_download_link(name, videourl, 'Play', img, name)

    nextp = re.compile('next" href="([^"]+)"', re.DOTALL | re.IGNORECASE).search(listhtml)
    if nextp:
        site.add_dir('Next Page', nextp.group(1), 'List', site.img_next)
    utils.eod()


@site.register()
def Tag(url):
    cathtml = utils.getHtml(url)
    match = re.compile(r'(tag/[^"]+)">\s+([^\)]+\))', re.IGNORECASE | re.DOTALL).findall(cathtml)
    for caturl, name in match:
        name = utils.cleantext(name)
        site.add_dir(name, site.url + caturl, 'List', '')
    utils.eod()


@site.register()
def Play(url, name, download=None):
    vp = utils.VideoPlayer(name, download=download)
    videohtml = utils.getHtml(url)
    match = re.compile('iframe src="([^"]+)"', re.IGNORECASE | re.DOTALL).search(videohtml)
    if match:
        iframeurl = match.group(1)
        if 'xtremestream' in iframeurl:
            headers = {'Referer': iframeurl}
            iframehtml = utils.getHtml(iframeurl, url)
            videoid = re.compile(r"""var video_id\s+=\s+[`'"]([^`'"]+)[`'"];\s+var m3u8_loader_url\s=\s[`'"]([^`'"]+)[`'"];""", re.IGNORECASE | re.DOTALL).findall(iframehtml)[0]
            #videourl = videoid[1] + videoid[0] + "|{0}".format(urllib_parse.urlencode(headers))

            m3u8html = utils.getHtml(videoid[1] + videoid[0], iframeurl)
            videourl = re.compile("(https://[^\n]+)$", re.IGNORECASE | re.DOTALL).findall(m3u8html)[0]
            videourl = "{0}|{1}".format(videourl, urllib_parse.urlencode(headers))
            vp.play_from_direct_link(videourl)
        else:
            utils.notify('Oh oh', 'No other video hosts supported yet')
    else:
        utils.notify('Oh oh', 'No video found')