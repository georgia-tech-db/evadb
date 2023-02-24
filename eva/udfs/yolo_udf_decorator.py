from eva.udfs.abstract.udf_declaration import UDF

yolo_udf = UDF(cache=True)


@yolo_udf.setup(
    model_type="object_dectection_yolo", 
    threshold=0.85
)
def setup():
    pass

    
@yolo_udf.forward()
def forward_fn(self, frames_arr):
    outcome = []
    # for i in range(frames_arr.shape[0]):
    #     single_result = predictions.pandas().xyxy[i]
    #     pred_class = single_result["name"].tolist()
    #     pred_score = single_result["confidence"].tolist()
    #     pred_boxes = single_result[["xmin", "ymin", "xmax", "ymax"]].apply(
    #         lambda x: list(x), axis=1
    #     )

    #     outcome.append(
    #         {
    #             "labels": pred_class,
    #             "bboxes": pred_boxes,
    #             "scores": pred_score,
    #         }
    #     )
    
    return outcome
        
                
        
