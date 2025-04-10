#  - IPL Team Optimization Project

## 📌 Project Title
**Optimizing IPL Team Selection Using Machine Learning and Genetic Algorithms**

---

## 🧠 Introduction

This project presents a comprehensive machine learning and optimization framework to select the **best-performing Indian Premier League (IPL) team** while adhering to league constraints such as player roles, overseas limits, and squad size. It applies **Genetic Algorithms**, **Simulated Annealing**, and a **Greedy Algorithm** to automate and enhance the team-building process using real IPL data.

---

## 🎯 Objectives

- Build an optimized IPL squad of 17 players.
- Maintain role distribution: Batsmen, Bowlers, All-Rounders, Wicketkeepers.
- Limit overseas players to a maximum of 6.
- Maximize fitness based on batting, bowling, and all-rounder metrics.

---

## 🔁 Project Workflow

- **Data Cleaning**: Preprocessed CSV files from Kaggle IPL dataset.
- **Feature Engineering**: Derived metrics like `strike_rate`, `boundary_percentage`, `economy_rate`, `all_rounder_index`.
- **Role Assignment**: Assigned player roles based on performance thresholds.
- **Data Merging**: Unified datasets into one master file.
- **Optimization**: Applied Genetic Algorithm, Simulated Annealing, and Greedy Algorithm.
- **Evaluation**: Compared outputs via visualizations and fitness scores.

---

## ⚙️ Technologies Used

- Python
- NumPy, Pandas
- Matplotlib, Seaborn
- Scikit-learn
- DEAP (Genetic Algorithms)
- Jupyter Notebook / VS Code

---

## 🧬 Optimization Techniques

- **Genetic Algorithm (GA)**:  
  Mimics evolution through selection, crossover, mutation. Best overall performance and team balance.

- **Simulated Annealing (SA)**:  
  Probabilistic technique to escape local optima. Performed moderately well with fewer resources.

- **Greedy Algorithm**:  
  Simple and fast. Lower performance, good for quick approximations.

---

## 📂 Dataset

Kaggle - IPL CSV Dataset  
🔗 [https://www.kaggle.com/harsha547/indian-premier-league-csv-dataset](https://www.kaggle.com/harsha547/indian-premier-league-csv-dataset)

---
