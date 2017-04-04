package org.eu.multiply.auxdata.dummy;

/**
 * @author Tonio Fincke
 */
public class DummyAuxDataProvider implements AuxDataProvider {

    public AuxData readAuxData(String constraints) {
        return new DummyAuxData();
    }
}
