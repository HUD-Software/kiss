namespace Kiss.Project
{
    public class Interface
    {
        public Interface(string directory, string name)
        {
            Path = System.IO.Path.Join(directory, "interfaces", name);
        }

        public FileStream AddNewFile(string name)
        {
            var file = File.Create(System.IO.Path.Join(Path, name));
            _files.Add(name);
            return file;
        }

        public string Path { get; init; }

        public IEnumerable<string> Files => _files;

        private List<string> _files = new List<string>();   
    }
}
