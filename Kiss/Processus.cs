using System;
using System.Diagnostics;

namespace Kiss
{
    internal class Exec
    {

        public static int RunProcess(string program, string[] args, string? workingDir = null, Dictionary<string, string>? env = null)
        {
            using (Process proc = new Process())
            {
                proc.StartInfo.FileName = program;
                proc.StartInfo.UseShellExecute = false;
                proc.StartInfo.CreateNoWindow = true;
                if (env is not null)
                {
                    foreach (var keyValue in env)
                        proc.StartInfo.Environment.Add(keyValue.Key, keyValue.Value);
                }
                proc.StartInfo.WorkingDirectory = workingDir ?? Directory.GetCurrentDirectory();
                proc.StartInfo.Arguments = String.Join(" ", args);

                proc.StartInfo.RedirectStandardOutput = true;
                proc.StartInfo.RedirectStandardError = true;
                proc.OutputDataReceived += new DataReceivedEventHandler(
                    (object sendingProcess, DataReceivedEventArgs outLine) =>
                    {
                        if (outLine.Data is not null)
                        {
                            Logs.PrintLine(outLine.Data);
                        }
                    });
                proc.ErrorDataReceived += new DataReceivedEventHandler(
                    (object sendingProcess, DataReceivedEventArgs outLine) =>
                    {
                        if (outLine.Data is not null)
                        {
                            Logs.PrintErrorLine(outLine.Data);
                        }
                    });
                proc.Start();

                // proc.BeginOutputReadLine();
                // proc.BeginErrorReadLine();
                // proc.WaitForExit();
                while (!proc.HasExited)
                {
                    string? outputLine;
                    do
                    {
                        outputLine = proc.StandardOutput.ReadLine();
                        if (!String.IsNullOrEmpty(outputLine))
                        {
                            Logs.PrintLine(outputLine);
                        }
                    }
                    while (!String.IsNullOrEmpty(outputLine));

                    string errorLine;
                    do
                    {
                        errorLine = proc.StandardError.ReadToEnd();
                        if (!String.IsNullOrEmpty(errorLine))
                        {
                            Logs.PrintError(errorLine);
                        }
                    } while (!String.IsNullOrEmpty(errorLine));
                }

                return proc.ExitCode;
            }   
        }
    }
}
