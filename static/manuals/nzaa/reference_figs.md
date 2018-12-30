Referencing figures in a text
=============================

    [[filename.jpg Everything after the first space is a caption.]]

When compiling a new site record, or updating an existing one, it is
often necessary to include figures; drawings, maps or photographs, in
the body of your record. You can achieve this by first uploading an
image file (.png, .jpg, .svg etc) to your record, and then inserting a
simple code which will tell the Archaeography server to present the
image file and your caption in the text of the record.

To refer to an inline file in the text of a record:

1.  Upload the file

2.  Encase the filename and caption in double-square brackets:

        [[filename.jpg Everything after the first space is a caption.]]

This can be done in text fields, in a site update or new site
record. These fields are 'Introduction", 'Aid to relocation',
'Description', 'Condition statement', 'References' and 'Rights'.

When you view your record, the image file will appear at the point of
the text where this reference is. For the technically-minded, this
line is replaced with the following HTML code (you can see it, by
viewing the source of the web page in your browser):

    <div class='figure'>

        <img src='/path/to/filename.jpg' />

        <p class='caption'>Everything after the first space is a caption.</p>

    </div>


The filename may not contain spaces. Spaces in filenames are replaced
with the underscore character ('_') when you upload a file to a new
site record, or a site update record.


