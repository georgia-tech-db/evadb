
#get the optimal plan
#go to the children attribute
#types seqscan, project, predicate, lateral join, functional scan

#target list has the list of columns that need to be selected

#Lateral Join: Children traverse sequential and join.
#Seq Scan: 


from eva.planner import SeqScanPlan, LateralJoinPlan, StoragePlan, FunctionScanPlan, ProjectPlan
from eva.utils import singledispatchmethod
from eva.optimizer import ColumnMapper

class ColumnDeriver:

    def __init__(self):
        pass

    def merge(self, left_list, left_map, right_list, right_map):
        merged_list = left_list[:]
        merged_map = left_map
        attribute_id_counter = len(left_list)
        
        #merging the two lists
        new_map = {}
        for col_name, col_id in right_map:
            if col_name in left_map:
                new_map[col_id] = left_map[col_name]
            else:
                new_map[col_id] = attribute_id_counter
                merged_map[col_name] = attribute_id_counter
                attribute_id_counter+=1
        
        for index, id_val in enumerate(right_list):
            right_list[index] = new_map[id_val]
        
        merged_list.extend(right_list)

        return merged_list, merged_map
    
    @singledispatchmethod
    def scan_node_for_attributes(self, node, alias_prefix=None):
        raise NotImplementedError(f"Cannot bind {type(node)}")

    @scan_node_for_attributes.register(ProjectPlan)
    def scan_node_for_attributes(self, node, alias_prefix=None):
        child_nodes = node.children
        if len(child_nodes)>0:
            column_to_id_mapping_list, column_to_id_map = \
                self.scan_node_for_attributes(child_nodes[0], alias_prefix)

        return column_to_id_mapping_list, column_to_id_map
    
    @scan_node_for_attributes.register(StoragePlan)
    def scan_node_for_attributes(self, node, alias_prefix=None):
        video_columns = node.columns
        column_name_to_id_mapping = {}
        column_to_id_mapping_list = []
        attribute_id_counter = 0

        for column in video_columns:
            if alias_prefix:
                column_name = alias_prefix+column.name
            if column_name not in column_name_to_id_mapping:
                column_name_to_id_mapping[column_name] = attribute_id_counter
                column_to_id_mapping_list.append(attribute_id_counter)
                attribute_id_counter+=1
        
        return column_to_id_mapping_list, column_name_to_id_mapping

    @scan_node_for_attributes.register(SeqScanPlan)
    def scan_node_for_attributes(self, node, alias_prefix=None):
        alias_name = node.alias_name
        id_list, id_map = self.scan_node_for_attributes(node.children[0], alias_name)
        
        return id_list, id_map

    @scan_node_for_attributes.register(LateralJoinPlan)
    def scan_node_for_attributes(self,node, alias_prefix=None):
        left_child_list, left_child_map = self.scan_node_for_attributes(node.children[0], alias_prefix)
        right_child_list, right_child_map = self.scan_node_for_attributes(node.children[1], alias_prefix)
        merged_id_map, merged_attribute_id_list = \
            self.merge(left_child_list, left_child_map, right_child_list, right_child_map)
        
        return merged_id_map, merged_attribute_id_list


    def __call__(self, node):
        column_to_id_map, column_to_id_list = self.scan_node_for_attributes(node)
        column_mapper = ColumnMapper(column_to_id_map, column_to_id_list)
        updated_node = column_mapper.map_nodes_to_attributes(node)
        return updated_node





        

        

        




        

    