from __future__ import annotations

from mteb.abstasks.TaskMetadata import TaskMetadata

from .....abstasks import AbsTaskT2IRetrieval


class MSCOCOT2IRetrieval(AbsTaskT2IRetrieval):
    metadata = TaskMetadata(
        name="MSCOCOT2IRetrieval",
        description="Retrieve captions based on images.",
        reference="https://link.springer.com/chapter/10.1007/978-3-319-10602-1_48",
        dataset={
            "path": "MRBench/mbeir_mscoco_task0",
            "revision": "cfe15bd2791dde5f8f20aebecf0b4eb3812972d6",
            "trust_remote_code": True,
        },
        type="Retrieval",
        category="t2i",
        eval_splits=["test"],
        eval_langs=["eng-Latn"],
        main_score="ndcg_at_10",
        date=("2018-01-01", "2018-12-31"),
        form=["written"],
        domains=["Encyclopaedic"],
        task_subtypes=["Image Text Retrieval"],
        license="CC BY-SA 4.0",
        socioeconomic_status="medium",
        annotations_creators="derived",
        dialect=[],
        text_creation="found",
        bibtex_citation="""@inproceedings{lin2014microsoft,
  title={Microsoft coco: Common objects in context},
  author={Lin, Tsung-Yi and Maire, Michael and Belongie, Serge and Hays, James and Perona, Pietro and Ramanan, Deva and Doll{\'a}r, Piotr and Zitnick, C Lawrence},
  booktitle={Computer Vision--ECCV 2014: 13th European Conference, Zurich, Switzerland, September 6-12, 2014, Proceedings, Part V 13},
  pages={740--755},
  year={2014},
  organization={Springer}
}""",
        n_samples={"test": 1172},
        avg_character_length={
            "test": {
                "average_document_length": 30.94235294117647,
                "average_query_length": 131.56569965870307,
                "num_documents": 9350,
                "num_queries": 1172,
                "average_relevant_docs_per_query": 1.0,
            }
        },
    )