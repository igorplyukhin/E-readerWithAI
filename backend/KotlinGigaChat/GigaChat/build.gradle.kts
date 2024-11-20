plugins {
    kotlin("jvm") version "2.0.20"
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.squareup.okhttp3:okhttp:5.0.0-alpha.14")
    implementation("org.apache.pdfbox:pdfbox:3.0.3")
    implementation("org.json:json:20240303")

}

tasks.test {
    useJUnitPlatform()
}
kotlin {
    jvmToolchain(21)
}