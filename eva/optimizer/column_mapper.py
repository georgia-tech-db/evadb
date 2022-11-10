
from eva.planner.function_scan_plan import FunctionScanPlan
from eva.planner.seq_scan_plan import SeqScanPlan
from eva.planner.lateral_join_plan import LateralJoinPlan
from eva.planner.storage_plan import StoragePlan
from eva.planner.project_plan import ProjectPlan
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.abstract_expression import AbstractExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.utils.single_dispatch_method import singledispatchmethod


class ColumnMapper:
    """
    Maps the ids for columns
    """
    
    def __init__(self, column_to_id_map: dict, updated_col_map: dict):
        self.column_to_id_map = column_to_id_map
        self.updated_col_map = updated_col_map

    @singledispatchmethod
    def map_node_attributes_to_id(self, node: AbstractPlan):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    def map_children(self, children_list:list) -> list:
        for i, child in enumerate(children_list):
            children_list[i] = self.map_node_attributes_to_id(child)
        return children_list

    @map_node_attributes_to_id.register(AbstractPlan)
    def __map_abstract_plan(self, node: AbstractPlan) -> AbstractPlan:
        return node

    @map_node_attributes_to_id.register(ProjectPlan)
    def _map_project_plan(self, node: ProjectPlan) -> AbstractPlan:
        child_nodes = node.children
        node.children = self.map_children(child_nodes)

        #update the ids for columns in the target_list
        for i in range(len(node.target_list)):
            curr_node = node.target_list[i]
            column_name = curr_node.col_alias
            curr_node._col_idx = self.updated_col_map[column_name]
            node.target_list[i] = curr_node

        return node
    
    @map_node_attributes_to_id.register(StoragePlan)
    def __map_storage_plan(self, node: StoragePlan) -> AbstractPlan:
        for i in range(len(node.predicate.children)):
            child_node = node.predicate.children[i]
            node.predicate.children[i] = self.map_node_attributes_to_id(child_node)
        return node
    
    @map_node_attributes_to_id.register(TupleValueExpression)
    def _map_tuple_val_expr(self, node: TupleValueExpression) -> AbstractExpression:
        column_name = node.col_alias
        node._col_idx = self.column_to_id_map[column_name]
        return node

    @map_node_attributes_to_id.register(ConstantValueExpression)
    def _map_const_val_expr(self, node: ConstantValueExpression) -> AbstractExpression:
        return node

    @map_node_attributes_to_id.register(SeqScanPlan)
    def _map_seq_scan_plan_node(self, node: SeqScanPlan) -> AbstractPlan:
        node.children = self.map_children(node.children)
        return node

    @map_node_attributes_to_id.register(LateralJoinPlan)
    def _map_lateral_join_plan(self, node: LateralJoinPlan) -> AbstractPlan:
        #assumes that the first element of children is the left child
        updated_left_child = self.map_node_attributes_to_id(node.children[0])
        updated_right_child = self.map_node_attributes_to_id(node.children[1])
        node.children = [updated_left_child, updated_right_child]
        return node

    @map_node_attributes_to_id.register(FunctionScanPlan)
    def _map_func_scan_plan(self, node: FunctionScanPlan) -> AbstractPlan:
        for child in node.func_expr.children:
            col_name = child.col_alias
            child._col_idx = self.column_to_id_map[col_name]
        
        #update the projection columns
        alias_prefix = node.func_expr.alias.alias_name
        col_names = node.func_expr.alias.col_names
        col_name_lst = []
        for col_name in col_names:
            col_name_lst.append(alias_prefix+'.'+col_name)
            
        for i,column in enumerate(node.func_expr.projection_columns):
            node.func_expr.projection_columns[i] = self.column_to_id_map[col_name_lst[i]]

        return node
        