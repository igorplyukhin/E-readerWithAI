package com.example.models

import org.simpleframework.xml.Attribute
import org.simpleframework.xml.Element
import org.simpleframework.xml.ElementList
import org.simpleframework.xml.Namespace
import org.simpleframework.xml.Root
import org.simpleframework.xml.Text

@Root(name = "FictionBook", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class FictionBook(

    @field:Element(name = "description", required = false)
    var description: Description? = null,

    @field:Element(name = "body", required = false)
    var body: Body? = null
)

@Root(name = "description", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Description(

    @field:Element(name = "title-info", required = false)
    var titleInfo: TitleInfo? = null,

    @field:ElementList(entry = "custom-info", inline = true, required = false)
    var customInfos: List<CustomInfo>? = null
)

@Root(name = "title-info", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class TitleInfo(

    @field:ElementList(entry = "genre", inline = true, required = false)
    var genres: List<String>? = null,

    @field:ElementList(entry = "author", inline = true, required = false)
    var authors: List<Author>? = null,

    @field:Element(name = "book-title", required = false)
    var bookTitle: String? = null,

    @field:Element(name = "annotation", required = false)
    var annotation: Annotation? = null,

    @field:Element(name = "keywords", required = false)
    var keywords: String? = null,

    @field:Element(name = "date", required = false)
    var date: String? = null,

    @field:Element(name = "coverpage", required = false)
    var coverPage: CoverPage? = null,

    @field:Element(name = "lang", required = false)
    var lang: String? = null,

    @field:Element(name = "sequence", required = false)
    var sequence: Sequence? = null
)

@Root(name = "custom-info", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class CustomInfo(

    @field:Attribute(name = "info-type", required = false)
    var infoType: String? = null,

    @field:Text(required = false)
    var value: String? = null
)

@Root(name = "annotation", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Annotation(

    @field:ElementList(entry = "p", inline = true, required = false)
    var paragraphs: List<String>? = null
)

@Root(name = "coverpage", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class CoverPage(

    @field:Element(name = "image", required = false)
    var image: Image? = null
)

@Root(name = "image", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Image(

    @field:Attribute(name = "href", required = false)
    var href: String? = null
)

@Root(name = "sequence", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Sequence(

    @field:Attribute(name = "name", required = false)
    var name: String? = null,

    @field:Attribute(name = "number", required = false)
    var number: String? = null
)

@Root(name = "author", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Author(

    @field:Element(name = "first-name", required = false)
    var firstName: String? = null,

    @field:Element(name = "last-name", required = false)
    var lastName: String? = null
)

@Root(name = "body", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Body(

    @field:ElementList(entry = "title", inline = true, required = false)
    var titles: List<Title>? = null, // Изменено на список заголовков

    @field:ElementList(entry = "section", inline = true, required = false)
    var sections: List<Section>? = null
)

@Root(name = "section", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Section(

    @field:ElementList(entry = "title", inline = true, required = false)
    var titles: List<Title>? = null, // Изменено на список заголовков

    @field:ElementList(entry = "p", inline = true, required = false)
    var paragraphs: List<String>? = null,

    @field:ElementList(entry = "section", inline = true, required = false)
    var sections: List<Section>? = null
)

@Root(name = "title", strict = false)
@Namespace(reference = "http://www.gribuser.ru/xml/fictionbook/2.0")
data class Title(

    @field:ElementList(entry = "p", inline = true, required = false)
    var paragraphs: List<String>? = null
)
