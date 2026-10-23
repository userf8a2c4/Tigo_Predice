// Abrir_Demo.exe: abre Demo_Tigo_Predice.html (en la misma carpeta) con el navegador predeterminado.
// No lleva archivos adentro ni extrae nada: así los antivirus no lo confunden con un instalador. Se compila con construir.ps1.
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Windows.Forms;

[assembly: AssemblyTitle("Tigo Predice - Abrir demo")]
[assembly: AssemblyProduct("Tigo Predice")]
[assembly: AssemblyVersion("1.0.0.0")]

static class Abrir
{
    [STAThread]
    static void Main()
    {
        string archivo = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Demo_Tigo_Predice.html");
        if (!File.Exists(archivo))
        {
            MessageBox.Show("No encuentro Demo_Tigo_Predice.html en esta carpeta. Descomprima el zip completo.", "Tigo Predice");
            return;
        }
        Process.Start(new ProcessStartInfo(archivo) { UseShellExecute = true });
    }
}
