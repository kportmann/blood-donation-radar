![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

# Blood Donation Radar - Switzerland

<p align="center">   
    <img src="demo/BloodDonationRadar.png" alt="logo" width=1000 >
</p>

## Introduction

Welcome to the Blood Donation Radar - Switzerland Dashboard! <br>
We are Benjamin and Kevin, students specialising in Artificial Intelligence and Machine Learning at HSLU. This is our Data Visualisation project. <br>
<br>
The idea for the project came by visiting the offical homepage of the Blutspende SRK Schweiz (https://www.blutspende.ch/de/blutspende), where they show a barometer for a region of Switzerland. <br>
<br>
We extended this information by creating the dashboard, which includes a Switzerland map and some graph views. <br>
<br>
We used <b>synthesised data</b> for the project, so please be aware this project is only for visualisation purposes and <b>contains no official data</b>!

## Walkthrough
To show you the main features, here is a quick walkthrough of our dashboard.

### Landing view
You can start by selecting the canton you live in and your blood type. This will set the filters to your preferences. The filters can also be changed in the dashboard. <br>
<p align="center">
    <img src="demo/landingView.gif" alt="landing view" width="1000">
</p>

### Map view
Shows an overview of the blood reserves in days for all of Switzerland by canton. <br>
<p align="center">
    <img src="demo/mapView.gif" alt="map view" width="1000">
</p>

### Status view
Displays the status of blood reserves by canton for all blood groups.<br>
<p align="center">
    <img src="demo/statusView.gif" alt="map view" width="1000">
</p>

### Graph view
This graph shows the blood shortage for selected blood groups and cantons over a specific time period. The threshold line makes it easy to see when the blood shortage occurred. <br>
<p align="center">
    <img src="demo/graphView.gif" alt="map view" width="1000">
</p>

### Data view
The datatable can be found here and can also be exported as a CSV file. <br>
<p align="center">
    <img src="demo/dataView.gif" alt="map view" width="1000">
</p>

## To run the app locally
To run the Dashboard locally, you can clone this repository and run the app:

```bash
git clone https://github.com/kportmann/blood-donation-radar.git
cd blood-donation-radar
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Have fun trying out!

