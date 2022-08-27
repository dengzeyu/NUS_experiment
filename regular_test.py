class A:
    def __init__(self, x):
        print("inside __init__()")
        self.y = x
  
    def __str__(self):
        print("inside __str__()")
        print("value of y:", str(self.y))
  
    def __call__(self):
        res = 0
        print("inside __call__()")
        print("adding 2 to the value of y")
        res = self.y + 2
        new_res = self.y + 4
        return res, new_res
          
  
      
# declaration of instance of class A
a = A(3)
  
# calling __str__() for a
a.__str__()
  
# calling __call__() for a 
r = a()
print(r)
  
# declaration of another instance
# of class A
b = A(10)
  
# calling __str__() for b
b.__str__()
  
# calling __call__() for b
r = b()
print(r)