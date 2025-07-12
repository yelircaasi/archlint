# ::: archlint.configuration
    options:
      members: false
      show_root_heading: true
      show_root_full_path: true

### ::: archlint.configuration.DocsConfig
    handler: python
    options:
        members:
          - allow_additional
          - file_per_directory
          - file_per_class
          - ignore
          - keep_double_underscore
          - md_dir
        inherited_members: false
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.configuration.ImportInfo
    handler: python
    options:
        members:
          - external
          - internal
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.configuration.ImportsConfig
    handler: python
    options:
        members:
          - internal_allowed_everywhere
          - external_allowed_everywhere
          - allowed
          - disallowed
          - grimp_cache
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.configuration.MethodsConfig
    handler: python
    options:
        members:
          - normal
          - ordering
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.configuration.UnitTestsConfig
    handler: python
    options:
        members:
          - allow_additional
          - file_per_directory
          - file_per_class
          - ignore
          - keep_double_underscore
          - md_dir
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false

### ::: archlint.configuration.Configuration
    handler: python
    options:
        members:
          - root_dir
          - module_root_dir
          - module_name
          - docs
          - imports
          - methods
          - tests
        inherited_members: false
        members_order: source
        show_root_full_path: false
        summary: false
        show_root_heading: true
        show_source: false
