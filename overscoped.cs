void ProcessOrder(Order order)
{
    Console.WriteLine(order.CustomerName);
}

public class Parent
{
    public class Child // No need to expose this publicly
    {
        public void Speak() => Console.WriteLine("Hello!");
    }
}

class Program
{
    static int sharedCounter = 0; // Accessible from anywhere in the class

    static void IncrementCounter()
    {
        sharedCounter++;
    }
}

public class Helper
{
    public void DoSomething() // This doesn't need to be public
    {
        Console.WriteLine("Doing something...");
    }
}

class Program
{
    void IncrementCounter()
    {
        int counter = 0; // Scope is limited to the method
        counter++;
    }
}
