import json
import os
from typing import Dict, Any, List, Union


def correct_value_by_type(value: Any, data_type: str) -> Any:
    """
    Correct value based on the data type.
    """
    if value is None:
        return None
    
    try:
        if data_type == "number":
            if isinstance(value, str):
                # Remove any non-numeric characters except dots and minus
                cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
                if cleaned:
                    return float(cleaned) if '.' in cleaned else int(cleaned)
            elif isinstance(value, (int, float)):
                return value
            return None
            
        elif data_type == "boolean":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ['true', '1', 'yes', 'có', 'đúng']
            elif isinstance(value, (int, float)):
                return bool(value)
            return False
            
        elif data_type == "string":
            if isinstance(value, str):
                return value.strip()
            else:
                return str(value) if value is not None else ""
                
        elif data_type == "enum":
            if isinstance(value, str):
                return value.strip()
            else:
                return str(value) if value is not None else ""
                
        elif data_type == "array":
            if isinstance(value, list):
                return value
            elif isinstance(value, str):
                # Try to parse as JSON array
                try:
                    return json.loads(value)
                except:
                    return [value]
            return []
            
        elif data_type == "image":
            if isinstance(value, list):
                return value
            elif isinstance(value, dict):
                return [value]
            elif isinstance(value, str):
                return [{"url": value, "description": ""}]
            return []
            
        else:
            return value
            
    except Exception:
        return value


def flatten_array_to_object(array_value: List[Dict]) -> Dict[str, Any]:
    """
    Convert an array of objects with 'key' and 'value' into a flat object.
    """
    result = {}
    
    for item in array_value:
        if not isinstance(item, dict):
            continue
            
        key = item.get('key', '')
        if not key:
            continue
            
        label = item.get('label', '')
        item_type = item.get('type', 'string')
        value = item.get('value')
        unit = item.get('unit')
        important = item.get('important')
        
        # Handle nested arrays recursively
        if isinstance(value, list) and item_type == 'array':
            # Check if it's a nested array of objects with key-value pairs
            if value and isinstance(value[0], dict) and 'key' in value[0]:
                nested_object = flatten_array_to_object(value)
                result[key] = nested_object
            else:
                # It's a simple array
                corrected_value = correct_value_by_type(value, item_type)
                result[key] = corrected_value
        else:
            # Correct the value based on type
            corrected_value = correct_value_by_type(value, item_type)
            result[key] = corrected_value
    
    return result


def normalize_group_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the group data structure according to the specified requirements.
    """
    normalized_data = {}
    
    for category_key, category_data in input_data.items():
        if not isinstance(category_data, dict):
            continue
            
        category_value = category_data.get('value', [])
        
        # Flatten the array value into an object
        if isinstance(category_value, list):
            flattened_data = flatten_array_to_object(category_value)
            normalized_data[category_key] = flattened_data
        else:
            # Handle non-array values
            normalized_data[category_key] = category_value
    
    return normalized_data


def save_normalized_data(normalized_data: Dict[str, Any], output_file: str):
    """
    Save the normalized data to a JSON file with proper formatting.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_data, f, ensure_ascii=False, indent=2)
    print(f"Normalized data saved to: {output_file}")


def main():
    """
    Main function to process the group.json file and create normalized output.
    """
    input_file = "data_explore/group.json"
    output_file = "data_explore/group_normalized.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found!")
        return
    
    try:
        # Load the original data
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print("Original data loaded successfully.")
        print(f"Number of top-level categories: {len(original_data)}")
        
        # Normalize the data
        normalized_data = normalize_group_data(original_data)
        
        print("Data normalization completed.")
        print(f"Number of normalized categories: {len(normalized_data)}")
        
        # Save the normalized data
        save_normalized_data(normalized_data, output_file)
        
        # Print some statistics
        print("\nNormalization Statistics:")
        print("-" * 40)
        
        # Count different types of properties
        type_counts = {}
        important_count = 0
        total_properties = 0
        
        for category_key, category_data in normalized_data.items():
            if isinstance(category_data, dict):
                for prop_key, prop_data in category_data.items():
                    total_properties += 1
                    if isinstance(prop_data, dict) and 'type' in prop_data:
                        data_type = prop_data['type']
                        type_counts[data_type] = type_counts.get(data_type, 0) + 1
                        
                        if prop_data.get('important'):
                            important_count += 1
        
        print(f"Total properties: {total_properties}")
        print(f"Property types found:")
        for prop_type, count in type_counts.items():
            print(f"  - {prop_type}: {count}")
        
        print(f"Important properties: {important_count}")
        
        # Show some examples
        print("\nExample normalized structure:")
        print("-" * 40)
        example_count = 0
        for category_key, category_data in normalized_data.items():
            if example_count >= 2:
                break
            print(f"Category: {category_key}")
            print(f"  Properties: {len(category_data) if isinstance(category_data, dict) else 1}")
            
            # Show first few properties
            if isinstance(category_data, dict):
                prop_count = 0
                for prop_key, prop_data in category_data.items():
                    if prop_count >= 3:
                        break
                    if isinstance(prop_data, dict):
                        print(f"    {prop_key}:")
                        print(f"      Value: {prop_data.get('value')}")
                        print(f"      Type: {prop_data.get('type')}")
                        if prop_data.get('unit'):
                            print(f"      Unit: {prop_data.get('unit')}")
                        if prop_data.get('important'):
                            print(f"      Important: {prop_data.get('important')}")
                    else:
                        print(f"    {prop_key}: {prop_data}")
                    prop_count += 1
            else:
                print(f"  Value: {category_data}")
            print()
            example_count += 1
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
