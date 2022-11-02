
from eva.planner.function_scan_plan import FunctionScanPlan
from eva.planner.seq_scan_plan import SeqScanPlan
from eva.planner.lateral_join_plan import LateralJoinPlan
from eva.planner.storage_plan import StoragePlan
from eva.planner.project_plan import ProjectPlan
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.expression.constant_value_expression import ConstantValueExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.utils.single_dispatch_method import singledispatchmethod


class ColumnMapper:
    
    def __init__(self, column_to_id_map, column_to_id_list):
        self.column_to_id_map = column_to_id_map
        self.column_to_id_list = column_to_id_list

    @singledispatchmethod
    def map_node_attributes_to_id(self, node):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    @map_node_attributes_to_id.register(AbstractPlan)
    def __map_node_attributes_to_id_abstract_plan(self, node):
        return node

    @map_node_attributes_to_id.register(ProjectPlan)
    def _map_node_attributes_to_id_project_plan(self, node):
        child_nodes = node.children
        if len(child_nodes)>0:
            updated_node = self.map_node_attributes_to_id(child_nodes[0])

        child_nodes[0] = updated_node
        node.children = child_nodes

        for i in range(len(node.target_list)):
            curr_node = node.target_list[i]
            node.target_list[i] = self.map_node_attributes_to_id(curr_node)

        return node
    
    @map_node_attributes_to_id.register(StoragePlan)
    def __map_node_attributes_to_id_storage_plan(self, node):
        for i in range(len(node.predicate.children)):
            child_node = node.predicate.children[i]
            node.predicate.children[i] = self.map_node_attributes_to_id(child_node)
        
        return node
    
    @map_node_attributes_to_id.register(TupleValueExpression)
    def _map_node_attributes_to_id_tuple_val_expr(self, node):
        column_name = node.col_alias
        node._col_idx = self.column_to_id_map[column_name]
        return node

    @map_node_attributes_to_id.register(ConstantValueExpression)
    def _map_node_attributes_to_id_const_val_expr(self,node):
        return node

    @map_node_attributes_to_id.register(SeqScanPlan)
    def _map_node_attributes_to_id_seq_scan_plan_node(self, node):
        updated_child_node = self.map_node_attributes_to_id(node.children[0])
        node.children = [updated_child_node]
        return node

    @map_node_attributes_to_id.register(LateralJoinPlan)
    def _map_node_attributes_to_id_lateral_join_plan(self, node):
        updated_left_child = self.map_node_attributes_to_id(node.children[0])
        updated_right_child = self.map_node_attributes_to_id(node.children[1])
        node.children = [updated_left_child, updated_right_child]
        return node

    @map_node_attributes_to_id.register(FunctionScanPlan)
    def _map_node_attributes_to_id_func_scan_plan(self, node):
        for child in node.func_expr.children:
            col_name = child.col_alias
            child._col_idx = self.column_to_id_map[col_name]
        
        return node
        