# Best Practices

1. General
   1. Use four spaces for indentation.
   2. Use four space hanging indentation rather than vertical alignment
   3. Use underscores, not camelCase, for variable, function and method names
   4. Django import order
        - Standard library import
        - Import from the core django
        - Import from the third library
        - Import from local app/library
   5. Use snake_case for file and folder names
   6. Classes
      1. It should have upper first letter
      2. It should be separated by 2 lines of spaces
   7. Methods
      1. separated by 1 line of space
2. Model
   1. Field names should be all lowercase, using underscores instead of camelCase.
   2. The order of model inner classes and standard methods should be as follows (noting that these are not all required):
       - All database fields
       - Custom manager attributes
       - class Meta
       - def __str__()
       - def save()
       - def get_absolute_url()
       - Any custom methods
   3. model names should be a singular noun.
3. Views
   1. Use only class based views(preferably generic views)

4. URLs
   1. Use underscore in URL pattern name rather than dashes.
        ```python
        # Example
        url(regex=’^add/$’, view = view.view_name, name = ‘underscored_name’)
        ```
5. Test
   1. All the test cases files and methods should start with 'test', else django won't find the tests to run.
   2. Always use different db for your test cases
