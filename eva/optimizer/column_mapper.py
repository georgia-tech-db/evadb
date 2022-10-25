
from eva.planner import SeqScanPlan, LateralJoinPlan, StoragePlan, ProjectPlan
from eva.utils import singledispatchmethod


class ColumnMapper:
    
    def __init(self, column_to_id_map, column_to_id_list):
        self.column_to_id_map = column_to_id_map
        self.column_to_id_list = column_to_id_list

    @singledispatchmethod
    def map_node_attributes_to_id(self, node, alias_prefix = None):
        raise NotImplementedError(f"Cannot bind {type(node)}")
    
    @map_node_attributes_to_id.register(ProjectPlan)
    def map_node_attributes_to_id(self, node, alias_prefix = None):
        child_nodes = node.children
        if len(child_nodes)>0:
            updated_node = self.map_node_attributes_to_id(child_nodes[0])

        child_nodes[0] = updated_node
        node.children = child_nodes
        return node
    
    @map_node_attributes_to_id.register(StoragePlan)
    def map_node_attributes_to_id(self, node, alias_prefix = None):
        video_columns = node.columns
        new_column_to_id_list = []

        for column_name in video_columns:
            if alias_prefix:
                column_name = alias_prefix+column_name
            
            column_id = self.column_to_id_map[column_name]
            new_column_to_id_list.append(column_id)
        
        #update the node
        node.columns = new_column_to_id_list
    
    @map_node_attributes_to_id.register(SeqScanPlan)
    def map_node_attributes_to_id(self, node, alias_prefix = None):
        alias_name = node.alias_name
        updated_child_node = self.map_node_attributes_to_id(node.children[0], alias_name)
        node.children = [updated_child_node]
        return node

    @map_node_attributes_to_id.register(LateralJoinPlan)
    def map_node_attributes_to_id(self, node, alias_prefix = None):
        updated_left_child = self.map_node_attributes_to_id(node.children[0], alias_prefix)
        updated_right_child = self.map_node_attributes_to_id(node.children[1], alias_prefix)
        node.children = [updated_left_child, updated_right_child]
        return node


    


        

    

        
        

    



