from eva.expression.constant_value_expression import ConstantValueExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.seq_scan_plan import SeqScanPlan
from eva.planner.lateral_join_plan import LateralJoinPlan
from eva.planner.storage_plan import StoragePlan
from eva.planner.function_scan_plan import FunctionScanPlan
from eva.planner.project_plan import ProjectPlan
from eva.utils.single_dispatch_method import singledispatchmethod
from eva.optimizer.column_mapper import ColumnMapper
import copy

class ColumnDeriver:

    def __init__(self):
        pass

    def merge(self, left_list, left_map, right_list, right_map):
        merged_list = left_list[:]
        merged_map = left_map
        attribute_id_counter = len(left_list)
        
        #merging the two lists
        new_map = {}
        for col_name, col_id in right_map.items():
            if col_name in left_map:
                new_map[col_id] = left_map[col_name]
            else:
                new_map[col_id] = attribute_id_counter
                merged_map[col_name] = attribute_id_counter
                attribute_id_counter+=1
        
        for index, id_val in enumerate(right_list):
            right_list[index] = new_map[id_val]
        
        merged_list.extend(right_list)

        return merged_map, merged_list
    
    @singledispatchmethod
    def scan_node_for_attributes(self, node):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    @scan_node_for_attributes.register(AbstractPlan)
    def _scan_node_for_attributes_for_abstract_plan(self, node):
        return {}, []

    @scan_node_for_attributes.register(ProjectPlan)
    def _scan_node_for_attributes_for_project_plan(self, node):
        child_nodes = node.children
        if len(child_nodes)>0:
            column_to_id_mapping_map, column_to_id_list = \
                self.scan_node_for_attributes(child_nodes[0])

        prev_map = column_to_id_mapping_map
        prev_list = copy.deepcopy(column_to_id_list)

        target_list = node.target_list
        for curr_node in target_list:
            temp_map, temp_list = self.scan_node_for_attributes(curr_node)
            column_to_id_mapping_map, column_to_id_list = self.merge(prev_list, prev_map, temp_list, temp_map)
            prev_map = column_to_id_mapping_map
            prev_list = copy.deepcopy(column_to_id_list)


        return column_to_id_mapping_map, column_to_id_list
    
    @scan_node_for_attributes.register(StoragePlan)
    def _scan_node_for_attributes_for_storage_plan(self, node):
        node_children = node.predicate.children
        column_name_to_id_mapping = {}
        column_to_id_mapping_list = []
        prev_list = []
        prev_map = {}

        for child in node_children:
            temp_map, temp_list = self.scan_node_for_attributes(child)
            column_name_to_id_mapping, column_to_id_mapping_list =\
                 self.merge(prev_list, prev_map, temp_list, temp_map)
            
            prev_map = column_name_to_id_mapping
            prev_list =copy.deepcopy(column_to_id_mapping_list)
            
        return column_name_to_id_mapping, column_to_id_mapping_list

    @scan_node_for_attributes.register(SeqScanPlan)
    def _scan_node_for_attributes_for_seq_scan_plan(self, node):
        id_map, id_list = self.scan_node_for_attributes(node.children[0])
        return id_map, id_list

    @scan_node_for_attributes.register(LateralJoinPlan)
    def _scan_node_for_attributes_for_lateral_join_plan(self,node):
        left_child_map, left_child_list = self.scan_node_for_attributes(node.children[0])
        right_child_map, right_child_list = self.scan_node_for_attributes(node.children[1])
        merged_id_map, merged_attribute_id_list = \
            self.merge(left_child_list, left_child_map, right_child_list, right_child_map)
        
        return merged_id_map, merged_attribute_id_list

    @scan_node_for_attributes.register(FunctionScanPlan)
    def _scan_node_for_attributes_for_seq_scan_plan(self, node):
        column_name_to_id_mapping = {}
        column_to_id_mapping_list = []
        prev_list = []
        prev_map = {}
        node_children = node.func_expr.children

        for child in node_children:
            temp_map, temp_list = self.scan_node_for_attributes(child)
            column_name_to_id_mapping, column_to_id_mapping_list =\
                 self.merge(prev_list, prev_map, temp_list, temp_map)
            
            prev_map = column_name_to_id_mapping
            prev_list =copy.deepcopy(column_to_id_mapping_list)
            
        
        return column_name_to_id_mapping, column_to_id_mapping_list

    @scan_node_for_attributes.register(TupleValueExpression)
    def _scan_node_for_attributes_tuple_value_expr(self, node):
        column_name_to_id_mapping = {}
        column_to_id_mapping_list = []
        attribute_id_counter = 0
        column_name = node.col_alias
        if column_name not in column_name_to_id_mapping:
            column_name_to_id_mapping[column_name] = attribute_id_counter
            column_to_id_mapping_list.append(attribute_id_counter)
            
        
        return  column_name_to_id_mapping, column_to_id_mapping_list

    @scan_node_for_attributes.register(ConstantValueExpression)
    def _scan_node_for_attributes_const_val_expr(self, node):
        return {}, []

    def __call__(self, node):
        column_to_id_map, column_to_id_list = self.scan_node_for_attributes(node)
        column_mapper = ColumnMapper(column_to_id_map, column_to_id_list)
        updated_node = column_mapper.map_node_attributes_to_id(node)
        return updated_node
