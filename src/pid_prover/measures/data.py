"""PID measures data and metadata."""
import pandas as pd
from typing import List

# Encoding: Y=satisfied, N=not satisfied, Y_2=bivariate only,
#           N_A=not applicable, Y_*=empirical, N_dd=pointwise, N_m=full-support
measures_data = {
    # Property order matches paper table
    # MIN  MMI  RDR  BROJA DELTA RED  IG   RAV  CT   RR   DEP  CCS  PM   SX   MES  DO   WEDGE ALPHA PREC
    "SR":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y",   "Y",   "Y"],
    "S0":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y",   "Y",   "Y"],
    "M0":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y_2","Y","Y", "Y", "N", "N_dd","N_dd","N","N", "Y",   "Y",   "Y"],
    "GP":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "N", "N_dd","N_dd","Y","Y", "Y",   "Y",   "Y"],
    "LP0":  ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "N", "N_dd","N_dd","N","N", "N",   "N",   "N"],
    "LP1":  ["Y", "Y", "Y", "N_A","N_A","N_A","N_A","N","N","N_A","N_A","N","N_dd","N_dd","N_A","N_A","N", "N",   "N"],
    "IID":  ["N", "N", "N", "Y",  "Y",  "Y", "N", "Y", "Y", "Y", "Y", "Y", "N", "N", "Y", "Y", "Y",   "Y",   "Y"],
    "ID":   ["N", "N", "N", "Y",  "Y",  "Y", "N", "Y", "Y", "N", "Y", "N", "N", "N", "Y", "Y", "N",   "N",   "N"],
    "TM":   ["N", "Y", "N", "N",  "N",  "N", "Y_*","N","Y", "N", "N", "N", "N", "N", "N", "N", "Y",   "N",   "N"],
    "TC":   ["N", "N", "N", "N",  "N",  "N", "N", "N", "N", "N", "N", "N", "Y", "Y", "N", "N", "N",   "N",   "N"],
    "SE":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "N", "N", "Y",   "Y",   "Y"],
    "LB":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y_2","Y","Y", "Y", "N", "N", "N", "N", "N", "Y",   "Y",   "Y"],
    "TE":   ["Y", "Y", "Y_2","Y", "Y",  "Y", "Y", "Y_2","Y","Y", "Y", "N", "N", "N", "Y", "Y", "N",   "Y",   "Y"],
    "M1":   ["Y", "Y", "Y_2","Y", "Y",  "Y", "Y", "Y_2","Y","Y", "Y", "N", "N", "N", "N", "N", "N",   "Y",   "Y"],
    "S1":   ["N", "N", "N", "N",  "N",  "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N", "N",   "N",   "N"],
    "BB":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "N", "N", "N", "N", "N", "N", "N", "N", "Y", "Y", "Y",   "N",   "N"],
    "BP":   ["N", "N", "Y", "Y",  "Y",  "Y", "N", "N", "N", "N", "N", "N", "N_dd","N","N","N", "N",   "N",   "Y"],
    "AD":   ["N", "N", "N", "Y",  "N",  "N", "N", "N", "N", "N", "N", "N", "N", "N", "Y", "Y", "Y",   "Y",   "Y"],
    "CO":   ["Y", "Y", "Y", "Y",  "Y",  "N_m","Y","N", "Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "N",   "N",   "N"],
    "EI":   ["Y", "Y", "Y", "Y",  "Y",  "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y",   "Y",   "Y"],
}

measure_names: List[str] = [
    "I_min", "I_MMI", "I_RDR", "I_BROJA", "I_delta", "I_red",
    "I_IG", "I_RAV", "I_CT", "I_RR", "I_DEP", "I_CCS",
    "I_PM", "I_SX", "I_MES", "I_do", "I_wedge", "I_alpha", "I_prec"
]

# Measures only defined for bivariate (n=2) case
bivariate_only_measures: List[str] = ["I_BROJA", "I_delta", "I_red", "I_DEP"]

# Create DataFrame: rows=properties, columns=measures
measures_df: pd.DataFrame = pd.DataFrame(measures_data, index=measure_names).T
