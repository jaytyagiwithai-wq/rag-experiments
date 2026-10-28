Project Aurora: Autonomous Ocean Sensor Network
Fictional technical briefing for GraphRAG practice. All organizations, people, dates, and performance figures below are invented.

1. Overview
Project Aurora is a coastal monitoring initiative launched in March 2025 by the fictional Bluehaven Marine Institute (BMI). It deploys solar-powered sensor buoys to monitor temperature, salinity, dissolved oxygen, and microplastic concentration in the fictional North Pelican Bay.
2. Organizations and People
- Bluehaven Marine Institute (BMI) owns Project Aurora and maintains the sensor fleet.
- TideForge Robotics manufactures the Aster-4 buoy hardware under contract with BMI.
- CloudHarbor Analytics operates the data ingestion and anomaly-detection platform.
- Dr. Mira Sen, BMI's scientific director, leads the research program.
- Leo Navarro, TideForge's hardware lead, designed the Aster-4 power controller.
- Anika Rao, CloudHarbor's ML engineer, developed the ReefWatch anomaly detector.
3. Infrastructure
Each Aster-4 buoy contains four environmental sensors, a GPS module, a solar panel, and a satellite modem. Buoys send readings every 15 minutes through the PelicanSat satellite network to the HarborGate API, operated by CloudHarbor Analytics. HarborGate validates records and writes them to the CurrentDB time-series database. The ReefWatch model reads data from CurrentDB and produces anomaly alerts. Alerts appear in the Beacon Dashboard used by BMI researchers.
4. Deployment Timeline
- March 12, 2025: BMI approved Project Aurora.
- April 7, 2025: TideForge delivered 12 Aster-4 buoys.
- May 2, 2025: BMI deployed 8 buoys in North Pelican Bay; 4 remained as spares.
- June 18, 2025: CloudHarbor activated ReefWatch version 1.0.
- August 9, 2025: A storm damaged buoy A-07, causing a 36-hour data gap.
- August 12, 2025: TideForge replaced A-07's satellite modem.
- September 30, 2025: BMI published its first quarterly assessment.
5. Findings and Measurements
The first assessment covered May through September 2025. Mean water temperature increased from 21.4°C in May to 24.1°C in August, then decreased to 22.7°C in September. Dissolved oxygen fell below the project's warning threshold of 5.0 mg/L on 11 separate days. ReefWatch generated 43 alerts, of which researchers verified 31 as genuine environmental anomalies and 12 as false positives.
6. Incidents and Dependencies
The August 9 storm affected A-07 only. Because the buoy's satellite modem failed, HarborGate received no data from A-07 for 36 hours. ReefWatch could not evaluate A-07 during that interval, but the other seven deployed buoys continued reporting. The modem replacement restored transmissions on August 12.
7. Planned Improvements
BMI intends to add six more buoys in February 2026, subject to funding. CloudHarbor proposes ReefWatch 1.1 with adaptive thresholds to reduce false positives. TideForge proposes a redundant satellite modem for future Aster-4 revisions. None of these improvements had been deployed by the September 2025 assessment.
8. Explicit Relationships for Graph Extraction
- Project Aurora is owned by Bluehaven Marine Institute.
- Bluehaven Marine Institute contracts TideForge Robotics.
- TideForge Robotics manufactures Aster-4.
- Aster-4 transmits via PelicanSat.
- PelicanSat delivers readings to HarborGate API.
- HarborGate API stores records in CurrentDB.
- ReefWatch reads from CurrentDB.
- ReefWatch sends alerts to Beacon Dashboard.
- Dr. Mira Sen leads Project Aurora.
- Anika Rao developed ReefWatch.
- Leo Navarro designed Aster-4 power controller.
- Storm on August 9 damaged A-07.
- A-07 modem failure caused 36-hour data gap.
9. Suggested GraphRAG Evaluation Questions
1. Which company manufactures the devices used by Dr. Mira Sen's project?
2. Trace the path from an Aster-4 sensor reading to the researchers' dashboard.
3. Why was ReefWatch unable to detect anomalies from A-07 during the storm?
4. Who should collaborate to address both false alerts and communication failures?
5. How many buoys were deployed in May 2025, and how many remained as spares?
6. Were adaptive thresholds already running when BMI published its assessment?
7. What fraction of ReefWatch alerts were false positives?
8. Which organization owns the database used by the anomaly detector's upstream pipeline?
10. Data Caveats
All numerical measurements are simulated. A verified alert does not establish the underlying ecological cause. The proposed 2026 expansion is a plan, not a completed event. The 36-hour gap refers to A-07, not the entire fleet.