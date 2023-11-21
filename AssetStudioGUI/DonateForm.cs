using System.Windows.Forms;
using System.Drawing;

public class DonateForm : Form
{
    public DonateForm()
    {
        InitializeComponent();
    }

    private void InitializeComponent()
    {
        this.Icon = global::AssetStudioGUI.Properties.Resources._as;
        this.Size = new Size(613, 420);
        this.Text = "Donate to AssetStudio";

        Label label = new Label();
        label.Text = "AssetStudio is a free and open-source software.\nIf you like it and find it helpful, you can buy me a coffee!";
        label.AutoSize = false;
        label.Size = new Size(613, 50);
        label.Location = new Point(10, 10);
        label.Font = new Font(label.Font.FontFamily, 12, FontStyle.Regular);
        label.Padding = new Padding(0, 5, 0, 5);

        PictureBox pictureBox = new PictureBox();
        pictureBox.Size = new Size(573, 306);
        pictureBox.Location = new Point(10, 60);
        pictureBox.SizeMode = PictureBoxSizeMode.StretchImage;
        pictureBox.Image = global::AssetStudioGUI.Properties.Resources.donate;

        this.Controls.Add(label);
        this.Controls.Add(pictureBox);
    }
}