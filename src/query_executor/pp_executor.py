from src.models.storage.batch import FrameBatch


class PPExecutor:
    """
      Applies PP to filter out the frames that doesn't satisfy the condition
      Arguments:
          node (AbstractPlan): ...
      """

    def __init__(self, node: 'AbstractPlan'):
        super().__init__(node)
        self.PP_plan = node.PP_plan
        self.predicate = node.predicate

    def execute(self, batch: FrameBatch):
        filtered_frame = self.PP_plan.predict(batch)
        return filtered_frame
