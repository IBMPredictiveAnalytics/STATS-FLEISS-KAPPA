# STATS_FLEISS_KAPPA
## Compute Fleiss Multi-Rater Kappa Statistics.
Compute Fleiss Multi-Rater Kappa Statistics Provides overall estimate of kappa, along with asymptotic standard error, Z statistic, significance or p value under the null hypothesis of chance agreement and confidence interval for kappa. Also provides similar statistics for individual categories.

---
Requirements
----
- IBM SPSS Statistics 18 or later and the corresponding IBM SPSS Statistics-Integration Plug-in for Python.

---
Installation intructions
----
1. Open IBM SPSS Statistics
2. Navigate to Utilities -> Extension Bundles -> Download and Install Extension Bundles
3. Search for the name of the extension and click Ok. Your extension will be available.

---
Tutorial
----

### Installation Location

Analyze →

&nbsp;&nbsp;Scale →

&nbsp;&nbsp;&nbsp;&nbsp;Fleiss Kappa 

### UI
<img width="692" alt="image" src="https://user-images.githubusercontent.com/19230800/193654172-78070471-b510-43a0-ba58-7fc7ea7076f9.png">

### Syntax

```
DATASET ACTIVATE DataSet1.
STATS FLEISS KAPPA VARIABLES=salary jobtime
 /OPTIONS CILEVEL=95.
```
---
License
----

- [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
                              
Contributors
----

  - JKP, IBM SPSS
