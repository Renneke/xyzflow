####################
Getting Started
####################

You can write a flow in a few lines of code:

.. code-block:: python

    from xyzflow import Parameter

    # Define parameters
    x = Parameter(value=10, description="X")
    y = Parameter(value=10, description="Y")
    
    def main():
        return x + y
        
    if __name__ == "__main__":   
        print(main()()) # Execute flow and print the result

.. note::

    A flow consists out of:
        1) Parameter definitions in the global scope
        2) A `main()` method that returns the resulting Task
        3) Optionally: A main if clause that executes your defined flow

To run the flow you can simple call it from the terminal:

.. code-block:: bash

    $ python3 my_flow.py
    20
