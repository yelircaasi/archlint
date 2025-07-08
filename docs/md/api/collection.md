# ::: archlint.collection
    options:
      members: false
      show_root_heading: true
      show_root_full_path: true

### ::: archlint.collection.Objects
    handler: python
    options:
        show_root_full_path: false
        members:
        - classes
        - functions
        - function_strings
        - method_strings
        - methodless
        - strings
        - apply
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.collect_method_info
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.parse_function
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.collect_objects_in_md
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.collect_docs_objects
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false
        

### ::: archlint.collection.collect_object_texts
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.collect_source_objects
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.collection.add_inherited_methods
    handler: python
    options:
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false
