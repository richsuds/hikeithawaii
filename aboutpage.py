from flask import Flask, render_template, redirect, url_for, request, Blueprint
import bs4
import requests


about = Blueprint('about', __name__)

@about.route("/about")
def aboutinfo():
    info = "Hikeit Hawaii"
    summary = "Hawaii's Hiking Weather...Trail Conditions...and Waterfalls"
    island = "About"
    aboutus = "Hikeit Hawaii provides weather forecasts tailored for hikers in Hawaii. \
               Our site utilizes past weather observations as well as automated forecasts \
               to predict what the weather conditions will be for each trail or area. \
               In addition, Hikeit Hawaii predicts the likelihood of how muddy the trails are \
               and how full waterfalls will be flowing (experimental)."

    contact = "We appreciate any feedback, comments, or questions you may have. Please feel free to contact us at hikeithawaii@gmail.com."

    disclaimertitle = "Disclaimer:"
    disclaimer = "The conditions, observations, and forecasts provided by HikeIt Hawaii are for informational purposes only. \
                  Weather data collected from the National Weather Service could be outdated or inaccurate. \
                  Use caution and check all available resources before hiking. \
                  Under no circumstance are we, or any third party affiliates, liable for any loss or damage of any kind \
                  incurred as a result of the use of this site."

    return render_template('about.html',**locals())
