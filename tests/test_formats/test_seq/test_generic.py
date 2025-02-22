"""tests for the ``crowsetta.formats.seq.generic`` module

There's a lot in that module.
So this one uses classes to logically group testing the different classes + functions.
Classes here are in the same order as classes / functions in the ``crowsetta`` module.
"""
import pathlib

import pandas as pd
import pandera.errors
import pytest

import crowsetta


class TestGeneralSeqSchema:
    """tests for the ``GeneralSeqSchema`` class"""

    # these ``test_schema_good_format_csv`` tests are basically smoke tests
    # that make sure nothing breaks if/when we modify the schema.
    # "good" = it was working last time we tested this

    def test_schema_good_notmat_csv(self, notmat_as_generic_seq_csv):
        """test that we can validate a `'generic-seq'` format .csv
        generated by ``annot2csv``.
        We use the `'notmat'` format as an example of a format
        with onsets and offsets in seconds.
        """
        notmat_generic_seq_df = pd.read_csv(notmat_as_generic_seq_csv)
        df = crowsetta.formats.seq.generic.GenericSeqSchema.validate(notmat_generic_seq_df)
        # if validation worked, we should get back a DataFrame
        assert isinstance(df, pd.DataFrame)

    def test_schema_good_birdsongrec_csv(self, birdsongrec_as_generic_seq_csv):
        """test that we can validate a `'generic-seq'` format .csv
        generated by ``annot2csv``.
        We use the `'birdsong-recognition-dataset'` format as an example of a format
        with onsets and offsets in seconds and samples.
        """
        birdsongrec_generic_seq_df = pd.read_csv(birdsongrec_as_generic_seq_csv)
        df = crowsetta.formats.seq.generic.GenericSeqSchema.validate(birdsongrec_generic_seq_df)
        # if validation worked, we should get back a DataFrame
        assert isinstance(df, pd.DataFrame)

    def test_schema_good_phn_csv(self, timit_phn_as_generic_seq_csv):
        """test that we can validate a `'generic-seq'` format .csv
        generated by ``annot2csv``.
        We use the `'timit'` format as an example of a format
        with onsets and offsets in samples.
        """
        timit_phn_generic_seq_df = pd.read_csv(timit_phn_as_generic_seq_csv)
        df = crowsetta.formats.seq.generic.GenericSeqSchema.validate(timit_phn_generic_seq_df)
        # if validation worked, we should get back a DataFrame
        assert isinstance(df, pd.DataFrame)

    def test_missing_column_raises(self, csv_missing_fields_in_header):
        """test that missing column 'label' raises a schema error"""
        missing_df = pd.read_csv(csv_missing_fields_in_header)
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.GenericSeqSchema.validate(missing_df)

    def test_invalid_column_raises(self, csv_with_invalid_fields_in_header):
        """test that invalid column name 'invalid' raises a schema error"""
        invalid_df = pd.read_csv(csv_with_invalid_fields_in_header)
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.GenericSeqSchema.validate(invalid_df)

    def test_onset_s_with_no_offset_s_raises(self, csv_with_onset_s_but_no_offset_s):
        """test that an 'onset_s' column with no 'offset_s' column raises a schema error"""
        no_offset_s_df = pd.read_csv(csv_with_onset_s_but_no_offset_s)
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.GenericSeqSchema.validate(no_offset_s_df)

    def test_onset_sample_with_no_offset_sample_raises(self, csv_with_onset_sample_but_no_offset_sample):
        """test that an 'onset_sample' column with no 'offset_sample' column raises a schema error"""
        no_offset_sample_df = pd.read_csv(csv_with_onset_sample_but_no_offset_sample)
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.GenericSeqSchema.validate(no_offset_sample_df)

    def test_no_onset_or_offset_column_raises(self, csv_with_no_onset_or_offset_column):
        """test that **no** onset or offset columns raises a schema error"""
        no_onset_or_offset_column_df = pd.read_csv(csv_with_no_onset_or_offset_column)
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.GenericSeqSchema.validate(no_onset_or_offset_column_df)


class TestAnnot2DfFunction:
    """tests for ``annot2df`` function"""

    def test_annot2df_onset_offset_s_only(self, notmat_paths, notmat_as_generic_seq_csv):
        """test whether `annot2df` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'notmat' format.
        """
        annot_list = [crowsetta.formats.seq.NotMat.from_file(notmat_path).to_annot() for notmat_path in notmat_paths]
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = crowsetta.formats.seq.generic.annot2df(annot_list, basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_compare = pd.read_csv(notmat_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_annot2df_onset_offset_s_and_ind(
        self, birdsong_rec_xml_file, birdsong_rec_wav_path, birdsongrec_as_generic_seq_csv
    ):
        """test whether `annot2df` works when
        the annotations have onsets and offsets specified in seconds and in samples.
        To test this we use the 'birdsong-recognition-dataset' format.
        """
        birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        )
        annot_list = birdsongrec.to_annot()
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = crowsetta.formats.seq.generic.annot2df(annot_list, basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(birdsongrec_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_annot2df_onset_offset_sample_only(self, kaggle_phn_paths, timit_phn_as_generic_seq_csv):
        """test whether `annot2df` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'timit' format."""
        annot_list = [crowsetta.formats.seq.Timit.from_file(phn_path).to_annot() for phn_path in kaggle_phn_paths]

        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = crowsetta.formats.seq.generic.annot2df(annot_list, basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(timit_phn_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)


class TestAnnot2CsvFunction:
    """tests for ``annot2csv`` function"""

    def test_annot2csv_onset_offset_s_only(self, notmat_paths, notmat_as_generic_seq_csv, test_data_root, tmp_path):
        """test whether `annot2csv` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'notmat' format.
        """
        annot_list = [crowsetta.formats.seq.NotMat.from_file(notmat_path).to_annot() for notmat_path in notmat_paths]
        csv_path = tmp_path / "test.csv"
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        crowsetta.formats.seq.generic.annot2csv(annot_list, csv_path, basename=True)
        assert pathlib.Path(csv_path).exists()
        df_created = pd.read_csv(csv_path)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(notmat_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_annot2csv_onset_offset_s_and_ind(
        self, birdsong_rec_xml_file, birdsong_rec_wav_path, birdsongrec_as_generic_seq_csv, test_data_root, tmp_path
    ):
        """test whether `annot2csv` works when
        the annotations have onsets and offsets specified in seconds and in samples.
        To test this we use the 'birdsong-recognition-dataset' format.
        """
        birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        )
        annot_list = birdsongrec.to_annot()
        csv_path = tmp_path / "test.csv"
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        crowsetta.formats.seq.generic.annot2csv(annot_list, csv_path, basename=True)
        assert pathlib.Path(csv_path).exists()
        df_created = pd.read_csv(csv_path)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(birdsongrec_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_annot2csv_onset_offset_sample_only(
        self, kaggle_phn_paths, timit_phn_as_generic_seq_csv, test_data_root, tmp_path
    ):
        """test whether `annot2csv` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'timit' format."""
        annot_list = [crowsetta.formats.seq.Timit.from_file(phn_path).to_annot() for phn_path in kaggle_phn_paths]

        csv_path = tmp_path / "test.csv"
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        crowsetta.formats.seq.generic.annot2csv(annot_list, csv_path, basename=True)
        assert pathlib.Path(csv_path).exists()
        df_created = pd.read_csv(csv_path)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(timit_phn_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)


class TestCsv2AnnotFunction:
    """tests for ``csv2annot`` function"""

    # these ``test_csv2annot_good`` tests are basically smoke tests
    # that make sure nothing breaks if/when we modify the schema.

    def test_csv2annot_good_notmat_csv(self, notmat_as_generic_seq_csv, notmat_paths):
        """test that we can load a .csv generated by ``annot2csv``.
        We use `'notmat'` format as an example of a format
        with onsets and offsets in seconds.
        """
        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=notmat_as_generic_seq_csv)
        annots_from_notmats = [
            crowsetta.formats.seq.NotMat.from_file(notmat_path).to_annot() for notmat_path in notmat_paths
        ]

        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        # only compare seq because .csv files are saved with `basename=True`.
        # Saving the .csv files this way avoids any platform-dependent / path issues
        assert all(
            [
                annot_from_csv.seq == annot_from_notmat.seq
                for annot_from_csv, annot_from_notmat in zip(annots, annots_from_notmats)
            ]
        )

    def test_csv2annot_notmat_round_trip(self, notmat_paths, tmp_path):
        """test whether we can write a csv with `annot2csv`,
        load it with `csv2annot`, and have the ``Annotation``s be equal,
        i.e. complete a "round trip".
        Because we test for a "round trip",
        this test goes beyond whether we're just able to load
        an already-generated .csv.

        First we test with annotations that have onsets and offsets specified in seconds only.
        To do so we use the 'notmat' format.
        """
        annots_from_notmats = [
            crowsetta.formats.seq.NotMat.from_file(notmat_path).to_annot() for notmat_path in notmat_paths
        ]
        csv_path = tmp_path / "test.csv"
        # we do not set abspath / basename to True because we want to exactly reproduce the annotations
        crowsetta.formats.seq.generic.annot2csv(annots_from_notmats, csv_path)

        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=csv_path)
        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        assert all(
            [
                annot_from_csv == annot_from_notmat
                for annot_from_csv, annot_from_notmat in zip(annots, annots_from_notmats)
            ]
        )

    def test_csv2annot_good_birdsongrec_csv(
        self,
        birdsongrec_as_generic_seq_csv,
        birdsong_rec_xml_file,
        birdsong_rec_wav_path,
    ):
        """test that we can load a .csv generated by ``annot2csv``.
        We use `'birdsong-recognition-dataset'` format
        as an example of a format
        with onsets and offsets in both seconds and samples.
        """
        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=birdsongrec_as_generic_seq_csv)
        birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        )
        annots_from_birdsongrec = birdsongrec.to_annot()

        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        # only compare seq because .csv files are saved with `basename=True`.
        # Saving the .csv files this way avoids any platform-dependent / path issues
        assert all(
            [
                annot_from_csv.seq == annot_from_birdsongrec.seq
                for annot_from_csv, annot_from_birdsongrec in zip(annots, annots_from_birdsongrec)
            ]
        )

    def test_csv2annot_birdsongrec_round_trip(
        self,
        birdsong_rec_xml_file,
        birdsong_rec_wav_path,
        tmp_path,
    ):
        """test whether we can write a csv with `annot2csv`,
        load it with `csv2annot`, and have the ``Annotation``s be equal,
        i.e. complete a "round trip".
        Because we test for a "round trip",
        this test goes beyond whether we're just able to load
        an already-generated .csv.

        We use `'birdsong-recognition-dataset'` format
        as an example of a format
        with onsets and offsets in both seconds and samples.
        """
        annots_from_birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        ).to_annot()

        csv_path = tmp_path / "test.csv"
        # we do not set abspath / basename to True because we want to exactly reproduce the annotations
        crowsetta.formats.seq.generic.annot2csv(annots_from_birdsongrec, csv_path)

        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=csv_path)
        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        assert all(
            [
                annot_from_csv == annot_from_notmat
                for annot_from_csv, annot_from_notmat in zip(annots, annots_from_birdsongrec)
            ]
        )

    def test_csv2annot_good_timit_phn_csv(self, timit_phn_as_generic_seq_csv, kaggle_phn_paths):
        """test that we can load a .csv generated by ``annot2csv``.

        We use `'timit'` format as an example of a format
        with onsets and offsets in samples.
        """
        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=timit_phn_as_generic_seq_csv)
        annots_from_phns = [crowsetta.formats.seq.Timit.from_file(phn_path).to_annot() for phn_path in kaggle_phn_paths]

        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        # only compare seq because .csv files are saved with `basename=True`.
        # Saving the .csv files this way avoids any platform-dependent / path issues
        assert all(
            [
                annot_from_csv.seq == annot_from_notmat.seq
                for annot_from_csv, annot_from_notmat in zip(annots, annots_from_phns)
            ]
        )

    def test_csv2annot_timit_phn_round_trip(self, kaggle_phn_paths, tmp_path):
        """test whether we can write a csv with `annot2csv`,
        load it with `csv2annot`, and have the ``Annotation``s be equal,
        i.e. complete a "round trip".
        Because we test for a "round trip",
        this test goes beyond whether we're just able to load
        an already-generated .csv.

        We use `'timit'` format as an example of a format
        with onsets and offsets in samples.
        """
        annots_from_phns = [crowsetta.formats.seq.Timit.from_file(phn_path).to_annot() for phn_path in kaggle_phn_paths]
        csv_path = tmp_path / "test.csv"
        # we do not set abspath / basename to True because we want to exactly reproduce the annotations
        crowsetta.formats.seq.generic.annot2csv(annots_from_phns, csv_path)

        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=csv_path)
        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])
        assert all(
            [annot_from_csv == annot_from_notmat for annot_from_csv, annot_from_notmat in zip(annots, annots_from_phns)]
        )

    def test_csv2annot_example_user_annotation(self, example_user_format_as_generic_seq_csv):
        annots = crowsetta.formats.seq.generic.csv2annot(csv_path=example_user_format_as_generic_seq_csv)
        assert isinstance(annots, list)
        assert all([isinstance(annot, crowsetta.Annotation) for annot in annots])

    def test_csv2annot_missing_fields_raises(self, csv_missing_fields_in_header):
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.csv2annot(csv_path=csv_missing_fields_in_header)

    def test_csv2annot_invalid_fields_raises(self, csv_with_invalid_fields_in_header):
        with pytest.raises(pandera.errors.SchemaError):
            crowsetta.formats.seq.generic.csv2annot(csv_path=csv_with_invalid_fields_in_header)


class TestGenericSeqClass:
    def test_to_and_from_csv_seqlike_with_onset_offset_in_s(self, notmat_paths, tmp_path):
        """test that we can write a set of annotations to a csv,
        load from that csv, then compare the saved and loaded
        annotations and find they are the same

        here we test this with an annotation format that has
        the onsets and offsets specified in seconds, `'notmat'`
        """
        notmats = [crowsetta.formats.seq.NotMat.from_file(notmat_path) for notmat_path in notmat_paths]
        annots = [notmat.to_annot() for notmat in notmats]
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annots)
        csv_path = tmp_path / "test.csv"
        generic_seq.to_file(csv_path)
        other_generic_seq = crowsetta.formats.seq.GenericSeq.from_file(csv_path)
        assert generic_seq == other_generic_seq

    def test_to_and_from_csv_seqlike_with_onset_offset_in_s_and_ind(
        self, birdsong_rec_xml_file, birdsong_rec_wav_path, tmp_path
    ):
        """test that we can write a set of annotations to a csv,
        load from that csv, then compare the saved and loaded
        annotations and find they are the same

        here we test this with an annotation format that has
        the onsets and offsets specified in both seconds and sample number,
        `'birdsong-recognition-dataset'`
        """
        birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        )
        annots = birdsongrec.to_annot()
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annots)
        csv_path = tmp_path / "test.csv"
        generic_seq.to_file(csv_path)
        other_generic_seq = crowsetta.formats.seq.GenericSeq.from_file(csv_path)
        assert generic_seq == other_generic_seq

    def test_annot2df_onset_offset_s_only(self, notmat_paths, notmat_as_generic_seq_csv):
        """test whether `annot2df` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'notmat' format.
        """
        annot_list = [crowsetta.formats.seq.NotMat.from_file(notmat_path).to_annot() for notmat_path in notmat_paths]
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annot_list)
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = generic_seq.to_df(basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_compare = pd.read_csv(notmat_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_to_df_onset_offset_s_and_ind(
        self, birdsong_rec_xml_file, birdsong_rec_wav_path, birdsongrec_as_generic_seq_csv
    ):
        """test whether `GenericSeq.to_df` works when
        the annotations have onsets and offsets specified in seconds and in samples.
        To test this we use the 'birdsong-recognition-dataset' format.
        """
        birdsongrec = crowsetta.formats.seq.BirdsongRec.from_file(
            annot_path=birdsong_rec_xml_file, wav_path=birdsong_rec_wav_path, concat_seqs_into_songs=True
        )
        annot_list = birdsongrec.to_annot()
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annot_list)
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = generic_seq.to_df(basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(birdsongrec_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)

    def test_to_df_onset_offset_sample_only(self, kaggle_phn_paths, timit_phn_as_generic_seq_csv):
        """test whether `annot2df` works when
        the annotations have onsets and offsets specified in seconds only.
        To test this we use the 'timit' format."""
        annot_list = [crowsetta.formats.seq.Timit.from_file(phn_path).to_annot() for phn_path in kaggle_phn_paths]
        generic_seq = crowsetta.formats.seq.GenericSeq(annots=annot_list)
        # below, set basename to True so we can easily run tests on any system without
        # worrying about where audio files are relative to root of directory tree
        df_created = generic_seq.to_df(basename=True)

        assert isinstance(df_created, pd.DataFrame)
        df_created = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_created)

        df_compare = pd.read_csv(timit_phn_as_generic_seq_csv)
        df_compare = crowsetta.formats.seq.generic.GenericSeqSchema.validate(df_compare)
        pd.testing.assert_frame_equal(df_created, df_compare)
