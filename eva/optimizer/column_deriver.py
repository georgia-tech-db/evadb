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


class ColumnDeriver:
    """
    Derives the id for the column names in the optimal plans
    """

    def __init__(self):
        pass
    
    @singledispatchmethod
    def scan_node_for_attributes(self, node:AbstractPlan, alias_prefix:str=None) -> dict:
        raise NotImplementedError(f"Cannot bind {type(node)}")

    def scan_children(self, children:list, alias_prefix:str=None) -> dict:
        """
        Function to scan all the children of a node and create the mapping of column names 
        to id. 
        """
        prev_map = {}
        
        prev_merged = {}
        for child in children:
            curr_map, merged = self.scan_node_for_attributes(child, alias_prefix)
            prev_map.update(curr_map)
            prev_merged.update(merged)
        
        return prev_map, prev_merged

    def merge(self, map1, map2):
        fin_map = map1
        for key,val in map2.items():
            if key not in fin_map:
                fin_map[key] = val
        return fin_map

    @scan_node_for_attributes.register(AbstractPlan)
    def _for_abstract_plan(self, node:AbstractPlan, alias_prefix:str=None) -> dict:
        return {},{}

    @scan_node_for_attributes.register(ProjectPlan)
    def _for_project_plan(self, node:ProjectPlan, alias_prefix:str=None) -> dict:
        child_nodes = node.children
        return self.scan_children(child_nodes)
    
    @scan_node_for_attributes.register(StoragePlan)
    def _for_storage_plan(self, node:StoragePlan, alias_prefix:str=None):
        """
        Scans the children of the Storage Plan node. Also gets the columns from
        video object.
        Assumption: columns of video are placed after the columns of the childrens
        """
        node_children = node.predicate.children
        column_name_to_id_mapping = {}
        prev_map = {}

        prev_map, merged = self.scan_children(node_children)
            
        video_columns_map = {}
        attribute_id = 0
        video_columns = node.video.columns
        for column in video_columns:
            col_name = alias_prefix+"."+column.name
            video_columns_map[col_name] = attribute_id
            attribute_id+=1
        
        # #TODO: remove this logic after updating the catalog orderin
        video_columns_map = {"myvideo.id": 0, "myvideo.data":1, "myvideo.name": 2}
        
        
        column_name_to_id_mapping = self.merge(prev_map, video_columns_map)

        return column_name_to_id_mapping, merged

    @scan_node_for_attributes.register(SeqScanPlan)
    def _for_seq_scan_plan(self, node:SeqScanPlan, alias_prefix:str=None) -> dict:
        alias_prefix = node.alias.alias_name
        return self.scan_children(node.children, alias_prefix)

    @scan_node_for_attributes.register(LateralJoinPlan)
    def _for_lateral_join_plan(self,node:LateralJoinPlan, alias_prefix:str=None) -> dict:
        """
        Scans the left child first and then the right child. Makes the assumption
        that the left child is the first element of children and right child is the 
        second element of children
        """
        left_child_map, _ = self.scan_node_for_attributes(node.children[0], alias_prefix)
        right_child_map, _ = self.scan_node_for_attributes(node.children[1], alias_prefix)
        
        col_update_map = left_child_map.copy()
        merged_id_map = self.merge(left_child_map, right_child_map)
        

        #update column numbers
        
        attribute_id_counter = len(col_update_map)

        for key,_ in right_child_map.items():
            if key not in col_update_map:
                col_update_map[key] = attribute_id_counter
                attribute_id_counter+=1
        
        return merged_id_map, col_update_map

    @scan_node_for_attributes.register(FunctionScanPlan)
    def _for_func_scan_plan(self, node:FunctionScanPlan, alias_prefix:str=None) -> dict:
        """
        To map the columns in the FunctionScanPlan node to ids
        Gets the columns of the children node first, then gets the columns from 
        func_expr.
        Assumption: columns of func_expr.alias are placed after children's columns.
        """
        column_name_to_id_mapping = {}
        prev_map = {}
        node_children = node.func_expr.children
        children_column_map, merged = self.scan_children(node_children)
    
        #get the columns from alias.
        alias_prefix = node.func_expr.alias.alias_name
        col_names = node.func_expr.alias.col_names
        col_map = {}
        id_counter = 0
        prev_map = children_column_map

        for col_name in col_names:
            col_map[alias_prefix+"."+col_name] = id_counter
            id_counter+=1

        
        column_name_to_id_mapping = self.merge(prev_map, col_map)
        
        return column_name_to_id_mapping, merged

    @scan_node_for_attributes.register(TupleValueExpression)
    def _for_tuple_value_expr(self, node:TupleValueExpression, alias_prefix:str=None) -> dict:
        column_name_to_id_mapping = {}
        attribute_id_counter = 0
        column_name = node.col_alias

        if column_name not in column_name_to_id_mapping:
            column_name_to_id_mapping[column_name] = attribute_id_counter
            
        return  column_name_to_id_mapping, {}

    @scan_node_for_attributes.register(ConstantValueExpression)
    def _for_const_val_expr(self, node: ConstantValueExpression, alias_prefix:str=None) -> dict:
        return {}, {}

    def __call__(self, node):
        column_to_id_map, updated_col_map = self.scan_node_for_attributes(node)
        column_mapper = ColumnMapper(column_to_id_map, updated_col_map)
        updated_node = column_mapper.map_node_attributes_to_id(node)
        return updated_node
