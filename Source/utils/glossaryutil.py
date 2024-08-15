from google.cloud import translate_v3 as translate

class glossary():

    def __init__(self, logger, languagelist_all):
        self.logger = logger
        self.languagelist_all = languagelist_all

    def create_glossary(self,
                        project_id,
                        input_uri,
                        glossary_id,
                        timeout=180,
                        ):
        """
        Create a equivalent term sets glossary. Glossary can be words or
        short phrases (usually fewer than five words).
        https://cloud.google.com/translate/docs/advanced/glossary#format-glossary
        """
        client = translate.TranslationServiceClient()

        # Supported language codes: https://cloud.google.com/translate/docs/languages
        source_lang_code = ["en-US"]
        # target_lang_code = ["zh-Hant","zh-Hans","ja","de","fr","es","it","pl","ru","id","vi","th","ar","da","el","ko","pt","tr","nl","nb","sv","cs"]
        target_lang_code = self.languagelist_all
        location = "us-central1"  # The location of the glossary

        name = client.glossary_path(project_id, location, glossary_id)
        language_codes_set = translate.types.Glossary.LanguageCodesSet(
            language_codes=source_lang_code + target_lang_code
        )

        gcs_source = translate.types.GcsSource(input_uri=input_uri)

        input_config = translate.types.GlossaryInputConfig(gcs_source=gcs_source)

        glossary = translate.types.Glossary(
            name=name, language_codes_set=language_codes_set, input_config=input_config
        )

        parent = f"projects/{project_id}/locations/{location}"
        # glossary is a custom dictionary Translation API uses
        # to translate the domain-specific terminology.
        operation = client.create_glossary(parent=parent, glossary=glossary)

        result = operation.result(timeout)
        self.logger.info("Created: {}".format(result.name))
        self.logger.info("Input Uri: {}".format(result.input_config.gcs_source.input_uri))

    def delete_glossary(self,
                        project_id="YOUR_PROJECT_ID",
                        glossary_id="YOUR_GLOSSARY_ID",
                        timeout=180,
                        ):
        """Delete a specific glossary based on the glossary ID."""
        client = translate.TranslationServiceClient()

        name = client.glossary_path(project_id, "us-central1", glossary_id)

        operation = client.delete_glossary(name=name)
        result = operation.result(timeout)
        self.logger.info("Deleted: {}".format(result.name))

    def translate_text_with_glossary(self,
                                     text="YOUR_TEXT_TO_TRANSLATE",
                                     project_id="YOUR_PROJECT_ID",
                                     glossary_id="YOUR_GLOSSARY_ID",
                                     ):
        """Translates a given text using a glossary."""

        client = translate.TranslationServiceClient()
        location = "us-central1"
        parent = f"projects/{project_id}/locations/{location}"

        glossary = client.glossary_path(
            project_id, "us-central1", glossary_id  # The location of the glossary
        )

        glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

        # Supported language codes: https://cloud.google.com/translate/docs/languages
        response = client.translate_text(
            request={
                "contents": [text],
                "target_language_code": "de-DE",
                "source_language_code": "en-US",
                "parent": parent,
                "glossary_config": glossary_config,
            }
        )

        self.logger.info("Translated text: \n")
        for translation in response.glossary_translations:
            self.logger.info("result:{}".format(translation.translated_text))

    def get_glossary(self, project_id="YOUR_PROJECT_ID", glossary_id="YOUR_GLOSSARY_ID"):
        """Get a particular glossary based on the glossary ID."""

        client = translate.TranslationServiceClient()

        name = client.glossary_path(project_id, "us-central1", glossary_id)

        response = client.get_glossary(name=name)
        self.logger.info(u"Glossary name: {}".format(response.name))
        self.logger.info(u"Entry count: {}".format(response.entry_count))
        self.logger.info(u"Input URI: {}".format(response.input_config.gcs_source.input_uri))
    from google.cloud import translate

    def list_glossaries(self, project_id="YOUR_PROJECT_ID"):
        """List Glossaries."""

        client = translate.TranslationServiceClient()

        location = "us-central1"

        parent = f"projects/{project_id}/locations/{location}"

        # Iterate over all results
        glossarylist = []
        for glossary in client.list_glossaries(parent=parent):
            # print ('glossary element is',glossary)
            glossarylist.append(glossary.name.split("/")[5])
            self.logger.info("Name: {}".format(glossary.name))
            self.logger.info("Entry count: {}".format(glossary.entry_count))
            self.logger.info("Input uri: {}".format(glossary.input_config.gcs_source.input_uri))

            # Note: You can create a glossary using one of two modes:
            # language_code_set or language_pair. When listing the information for
            # a glossary, you can only get information for the mode you used
            # when creating the glossary.
            #for language_code in glossary.language_codes_set.language_codes:
                #print("Language code: {}".format(language_code))
        #print ('glossary list is', glossarylist)
        return glossarylist
