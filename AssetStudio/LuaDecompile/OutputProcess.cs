using System;
using System.Diagnostics;
using System.Text;

public class OutputProcess : Process
{
    private StringBuilder m_Output = new StringBuilder();
    private StringBuilder m_Error = new StringBuilder();
    
    public string Output => m_Output.ToString();
    public string Error => m_Error.ToString();

    public OutputProcess()
    {
        StartInfo.RedirectStandardOutput = true;
        StartInfo.RedirectStandardError = true;
        OutputDataReceived += OnProcessOutput;
        ErrorDataReceived += OnProcessError;
    }

    private void OnProcessOutput(object sender,DataReceivedEventArgs events)
    {
        if (!String.IsNullOrEmpty(events.Data))
        {
            m_Output.AppendLine(events.Data);
        }
    }

    private void OnProcessError(object sender, DataReceivedEventArgs events)
    {
        if (!String.IsNullOrEmpty(events.Data))
        {
            m_Error.AppendLine(events.Data);
        }
    }

    public new bool Start()
    {
        m_Output.Clear();
        bool success = base.Start();
        if (success)
        {
            BeginOutputReadLine();
            BeginErrorReadLine();
        }
        return success;
    }
}
