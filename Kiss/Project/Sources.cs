namespace Kiss.Project
{
    public class Source
    {
        public Source(string directory)
        {
            Path = System.IO.Path.Join(directory, "sources");
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
