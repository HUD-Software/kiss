namespace Kiss
{
    public class Logs
    {
        private static readonly object ConsoleWriterLock = new object();

        public static void Print(string content)
        {
            Print(content, ConsoleColor.White);
        }
        public static void PrintLine(string content)
        {
            PrintLine(content, ConsoleColor.White);
        }

        public static void PrintSuccess(string content)
        {
            Print(content, ConsoleColor.Green);
        }
        public static void PrintSuccessLine(string content)
        {
            PrintLine(content, ConsoleColor.Green);
        }

        public static void PrintError(string content)
        {
            Print(content, ConsoleColor.Red);
        }
        public static void PrintErrorLine(string content)
        {
            PrintLine(content, ConsoleColor.Red);
        }

        public static void PrintTips(string content)
        {
            Print(content, ConsoleColor.Yellow);
        }
        public static void PrintTipsLine(string content)
        {
            PrintLine(content, ConsoleColor.Yellow);
        }

        private static void Print(string content, ConsoleColor color)
        {
            lock (ConsoleWriterLock)
            {
                var temp = Console.ForegroundColor;
                Console.ForegroundColor = color;
                Console.Write(content);
                Console.ForegroundColor = temp;
            }
        }

        private static void PrintLine(string content, ConsoleColor color)
        {
            lock (ConsoleWriterLock)
            {
                var temp = Console.ForegroundColor;
                Console.ForegroundColor = color;
                Console.WriteLine(content);
                Console.ForegroundColor = temp;
            }
        }
    }
}
