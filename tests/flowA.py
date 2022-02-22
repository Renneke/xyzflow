from xyzflow import Parameter

  
def main():
    # Define parameters
    x = Parameter.create(value=10, name="XA")
    y = Parameter.create(value=10, name="YA")    
    z = x + y
    return z
       
if __name__ == "__main__":   
    print(main()()) # Execute flow and print the result
  