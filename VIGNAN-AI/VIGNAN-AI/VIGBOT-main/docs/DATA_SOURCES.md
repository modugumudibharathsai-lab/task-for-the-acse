# Data Sources & Public Dataset Attribution

This document details the external open-source datasets integrated into the **VIGBOT** student helpdesk intent classification pipeline to harden boundary detection against out-of-scope non-college queries and improve conversational small-talk handling.

---

## 1. Governance & Evaluation Isolation Guardrails

Public data integration is governed by strict isolation principles designed to guarantee benchmark integrity and protect evaluation validity:

1. **Dedicated File Isolation**: All ingested public data is written exclusively to [`data/public/public_extra.csv`](file:///C:/StudentHelpdesk/data/public/public_extra.csv) (`text,intent,lang,author`). Public rows are **strictly prohibited** from existing inside `data/authors/` or `data/intents.csv`.
2. **Author Attribution Guard**: Public rows are tagged with author labels `clinc150` or `massive`. These authors are strictly forbidden from appearing in any student or staff author files.
3. **Quota Independence**: Public rows **never count** toward human author quotas (`aman`, `pragna`, `sirisha`) or starter quotas (`agent`). Quotas are tracked exclusively on human-authored institutional data.
4. **Sequestered Test Author Isolation**: Public rows **never appear** in the held-out test author split ([`sridhar.csv`](file:///C:/StudentHelpdesk/data/authors/sridhar.csv)), which remains 100% human-authored and sequestered.
5. **Cross-Validation Training Fold Guarantee**: In Leave-One-Author-Out (LOAO) cross-validation across human training authors, public rows are **always placed in the training split of every fold**, exactly like `agent` starter seeds.
6. **Opt-In CLI Flag**: Public training data is enabled via the explicit `--use-public` flag in [`ml/train_intent.py`](file:///C:/StudentHelpdesk/ml/train_intent.py), keeping the default training pipeline off and reproducible.
7. **Intent & Language Cap**: Public data is capped at **150 rows per (intent, lang) slice** with fixed `random_state=42` to prevent out-of-scope or general queries from overwhelming institutional college helpdesk topics.

---

## 2. Ingested Datasets

### 2.1 CLINC150 (OOS-Eval)

* **Full Title**: An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction
* **Authors**: Stefan Larson, Anish Mahendran, Joseph J. Peper, Christopher Clarke, Andrew Lee, Parker Hill, Jonathan K. Kummerfeld, Kevin Leach, Michael A. Laurenzano, Lingjia Tang, Jason Mars
* **Affiliation**: Clinc AI / University of Michigan
* **Publication**: *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP 2019)*, pages 1311–1316.
* **Paper Link**: [https://aclanthology.org/D19-1131/](https://aclanthology.org/D19-1131/)
* **Repository**: [https://github.com/clinc/oos-eval](https://github.com/clinc/oos-eval)
* **License**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

#### Usage in VIGBOT
* **`out_of_scope` (English)**: Extracted from the official `oos_train` split (intent: `oos`). These represent genuine out-of-scope user queries that fall outside task-oriented conversational domains.
* **`greeting_smalltalk` (English)**: Extracted from small-talk intents within the `train` split:
  * `greeting`
  * `thank_you`
  * `goodbye`
* **Author Tag**: `clinc150`
* **Language Tag**: `en`

#### Attribution & Citation
```bibtex
@inproceedings{larson-etal-2019-evaluation,
    title = "An Evaluation Dataset for Intent Classification and Out-of-Scope Prediction",
    author = "Larson, Stefan and Mahendran, Anish and Peper, Joseph J. and
      Clarke, Christopher and Lee, Andrew and Hill, Parker and
      Kummerfeld, Jonathan K. and Leach, Kevin and Laurenzano, Michael A. and
      Tang, Lingjia and Mars, Jason",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)",
    month = nov,
    year = "2019",
    address = "Hong Kong, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/D19-1131",
    doi = "10.18653/v1/D19-1131",
    pages = "1311--1316"
}
```

---

### 2.2 MASSIVE (Amazon Multilingual NLU)

* **Full Title**: MASSIVE: A 1M-Example Multilingual Natural Language Understanding Dataset with 51 Typologically-Diverse Languages
* **Authors**: Jack FitzGerald, Christopher Hennerfeind, Jason Mercer, Ruhi Sarikaya
* **Affiliation**: Amazon Alexa AI
* **Publication**: *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 4255–4274, Dublin, Ireland, May 2022.
* **Paper Link**: [https://aclanthology.org/2022.acl-long.297/](https://aclanthology.org/2022.acl-long.297/)
* **Repository & Data Access**: [https://github.com/alexa/massive](https://github.com/alexa/massive) / Amazon S3 `amazon-massive-dataset-1.0.tar.gz`
* **License**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

#### Usage in VIGBOT
* **Target Locales**:
  * `en-US` $\rightarrow$ `lang: en`
  * `hi-IN` $\rightarrow$ `lang: hi`
  * `te-IN` $\rightarrow$ `lang: te`
* **`out_of_scope` (Multilingual `en`, `hi`, `te`)**: Ingested from non-college scenarios within the `train` partition:
  * `music`
  * `cooking`
  * `weather`
  * `takeaway`
  * `news`
  * `recommendation`
* **`greeting_smalltalk` (Multilingual `en`, `hi`, `te`)**: Ingested from greeting items within the `general` scenario:
  * `general_greet` (partition: `train`)
* **Author Tag**: `massive`

#### Attribution & Citation
```bibtex
@inproceedings{fitzgerald-etal-2022-massive,
    title = "{MASSIVE}: A 1{M}-Example Multilingual Natural Language Understanding Dataset with 51 Typologically-Diverse Languages",
    author = "FitzGerald, Jack and Hennerfeind, Christopher and Mercer, Jason and Sarikaya, Ruhi",
    booktitle = "Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = may,
    year = "2022",
    address = "Dublin, Ireland",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.acl-long.297",
    doi = "10.18653/v1/2022.acl-long.297",
    pages = "4255--4274"
}
```

---

## 3. Data Distribution in `public_extra.csv`

The data ingestion script [`ml/add_public_data.py`](file:///C:/StudentHelpdesk/ml/add_public_data.py) samples and caps records per (intent, lang) slice at 150 rows (`random_state=42`):

| Intent | Language | Author | Sourced From | Sampled Rows |
| :--- | :--- | :--- | :--- | :--- |
| `greeting_smalltalk` | `en` | `clinc150` | `train` (`greeting`, `thank_you`, `goodbye`) | 125 |
| `greeting_smalltalk` | `en` | `massive` | `train` (`general` $\rightarrow$ `general_greet`) | 25 |
| `greeting_smalltalk` | `hi` | `massive` | `train` (`general` $\rightarrow$ `general_greet`) | 25 |
| `greeting_smalltalk` | `te` | `massive` | `train` (`general` $\rightarrow$ `general_greet`) | 25 |
| `out_of_scope` | `en` | `clinc150` | `oos_train` (out-of-scope training queries) | 75 |
| `out_of_scope` | `en` | `massive` | `train` (music, cooking, weather, takeaway, news, recommendation) | 75 |
| `out_of_scope` | `hi` | `massive` | `train` (music, cooking, weather, takeaway, news, recommendation) | 150 |
| `out_of_scope` | `te` | `massive` | `train` (music, cooking, weather, takeaway, news, recommendation) | 150 |
| **Total** | | | | **650** |

