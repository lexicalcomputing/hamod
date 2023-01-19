# HAMOD
a High Agreement Multi-lingual Outlier Detection dataset

## Data

This site hosts a multi-lingual dataset comprising manually prepared data suitable for carrying out the **outlier detection** exercise.
Outlier detection is a task of selecting an *outlier*, a word that does not fit to the set of given words based on some (typically semantic) criteria.

### Examples

* *blue*, *red*, *green*, *yellow*, *orange*, *black*, *brown*, *white*, *table*. Obviously, the last word is the outlier: all the others are names of colours.
* *bricklayer*, *lawyer*, *shop assistant*, *gentleman*, *waitress*, *metheorologist*. *Gentleman* is the outlier word because it is not a job.

### Dataset format

The dataset consists of plain text files, each containing 8 lines of the in-domain words, a blank line, and 8 lines of outlier words. Each file therefore represents 8 exercises (by taking the 8 in-domain words and adding one out of the 8 outliers) for sets of 9 words, or many more exercises for shorter sets (such as 64 exercises for sets of 8 words, by choosing one out of the 8 outliers and removing one out of the 8 in-domain words).
An example file for English covering the set of birds:

```
swan
duck
seagull
eagle
dove
crow
stork
goose

monkey
salmon
grasshopper
fly
egg
plane
woman
cliff
```

## Motivation

The outlier detection task features very high agreement (typically over 90%) among human annotators and can be used e.g. for the evaluation of distributional thesauri.
Please read the papers referenced below for all the details.

## Languages

At the moment the dataset consists of the following languages:

 * Czech
 * German
 * English
 * Estonian
 * French
 * Italian
 * Slovak

If you would like to collaborate with us on adding a new language, please use the contact below. 

## Authors

This dataset was developed by [Lexical Computing](https://www.lexicalcomputing.com), particularly by (in alphabetical order) Michal Cukr, Ondřej Herman, Miloš Jakubíček, Vojtěch Kovář, Emma Romani and Pavel Rychlý.

## Contact

Please use [inquiries@sketchengine.eu](mailto:inquiries@sketchengine.eu) for any questions or requests.

## License

<img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" />

The dataset is licensed under the [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license.
Attribution in any research context shall be carried out by properly citing the papers referenced below.
We would appreciate if you let us know about any derived work.

## References

Romani, E. (2022). Building A Multilingual Outlier Detection Dataset For The Evaluation Of Distributional Thesauri And Word Embeddings. Master's thesis, University of Pavia. [PDF](https://www.sketchengine.eu/wp-content/uploads/Building_a_Multilingual_Outlier_Detectio.pdf)

Jakubíček, M., Romani, E., Rychlý, P., & Herman, O. (2021). Development of HAMOD: a High Agreement Multi-lingual Outlier Detection dataset. In RASLAN 2021 Recent Advances in Slavonic Natural Language Processing, 177. [PDF](https://nlp.fi.muni.cz/raslan/raslan21.pdf#page=185)

Rychlý, P. (2019). Evaluation of Czech Distributional Thesauri. In RASLAN 2019  Recent Advances in Slavonic Natural Language Processing, 137. [PDF](https://nlp.fi.muni.cz/raslan/raslan19.pdf#page=145)
