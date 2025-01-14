#  Copyright (c) 2021 Rikai Authors
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyspark.sql import Row, SparkSession
from pyspark.sql.types import (
    ArrayType,
    FloatType,
    IntegerType,
    StructField,
    StructType,
)

from rikai.spark.sql.schema import parse_schema
from rikai.spark.types import Box2dType
from rikai.types import Image


def check_ml_predict(spark: SparkSession, model_name: str):
    # TODO: Replace uri string with Image class after GH#90 is released with
    # the upstream spark
    df = spark.createDataFrame(
        [
            # http://cocodataset.org/#explore?id=484912
            Row(
                image=Image(
                    "http://farm2.staticflickr.com/1129/"
                    "4726871278_4dd241a03a_z.jpg"
                )
            ),
            # https://cocodataset.org/#explore?id=433013
            Row(
                image=Image(
                    "http://farm4.staticflickr.com/3726/"
                    "9457732891_87c6512b62_z.jpg"
                )
            ),
        ],
    )
    df.createOrReplaceTempView("df")

    predictions = spark.sql(
        f"SELECT ML_PREDICT({model_name}, image) as predictions FROM df"
    )
    predictions.show()
    assert predictions.schema == StructType(
        [
            StructField(
                "predictions",
                ArrayType(
                    StructType(
                        [
                            StructField(
                                "box",
                                Box2dType(),
                            ),
                            StructField("score", FloatType()),
                            StructField("label_id", IntegerType()),
                        ]
                    )
                ),
            ),
        ]
    )
    assert predictions.schema == StructType(
        [
            StructField(
                "predictions",
                parse_schema(
                    "array<struct<box:box2d, score:float, label_id:int>>"
                ),
            )
        ]
    )

    assert predictions.count() == 2
